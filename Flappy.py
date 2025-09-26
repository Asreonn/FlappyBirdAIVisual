import pygame
import neat
import time
import os
import random

pygame.font.init()

WIDTH = 500
HEIGHT = 800
PANEL_WIDTH = 360
WINDOW_WIDTH = WIDTH + PANEL_WIDTH
current_directory= os.path.dirname(os.path.abspath(__file__))

birdIMGs = [pygame.transform.scale2x(pygame.image.load(os.path.join(current_directory+"/imgs","bird1.png"))),
            pygame.transform.scale2x(pygame.image.load(os.path.join(current_directory+"/imgs","bird2.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join(current_directory+"/imgs","bird3.png")))]

pipeIMG = pygame.transform.scale2x(pygame.image.load(os.path.join(current_directory+"/imgs","pipe.png")))

BGIMG = pygame.transform.scale2x(pygame.image.load(os.path.join(current_directory+"/imgs","bg.png")))

baseIMG = pygame.transform.scale2x(pygame.image.load(os.path.join(current_directory+"/imgs","base.png")))

statFont = pygame.font.SysFont("comicsans",32)
panelTitleFont = pygame.font.SysFont("bahnschrift",36)
panelFont = pygame.font.SysFont("bahnschrift",20)
diagramLabelFont = pygame.font.SysFont("bahnschrift",14)
diagramMessageFont = pygame.font.SysFont("bahnschrift",18)

GENERATION = 0
BEST_SCORE = 0
EVENT_LOG = []
ACTIVE_CONFIG = None
WINDOW_SURFACE = None

INPUT_LABELS = {
    -1: "Bird Y",
    -2: "ΔTop",
    -3: "ΔBottom",
}

OUTPUT_LABELS = {
    0: "Flap",
}


def log_event(message):
    """Append a formatted event message to the shared event history."""
    EVENT_LOG.append(message)
    # keep only the most recent 10 entries for readability
    if len(EVENT_LOG) > 10:
        del EVENT_LOG[0]


def ensure_window():
    """Return a persistent pygame display surface sized for the main view."""
    global WINDOW_SURFACE
    current_surface = pygame.display.get_surface()
    if current_surface is None or current_surface.get_size() != (WINDOW_WIDTH, HEIGHT):
        WINDOW_SURFACE = pygame.display.set_mode((WINDOW_WIDTH, HEIGHT))
    else:
        WINDOW_SURFACE = current_surface
    return WINDOW_SURFACE


def _compute_node_layers(genome, config):
    """Return depth assignment for every node based on enabled connections."""
    if genome is None or config is None:
        return {}, {}

    input_keys = tuple(config.genome_config.input_keys)
    output_keys = tuple(config.genome_config.output_keys)

    enabled_connections = {
        key: cg for key, cg in genome.connections.items() if cg.enabled
    }

    node_ids = set(input_keys) | set(output_keys) | set(genome.nodes.keys())
    for in_node, out_node in enabled_connections.keys():
        node_ids.add(in_node)
        node_ids.add(out_node)

    depth_cache = {}

    def resolve_depth(node_id, stack):
        if node_id in depth_cache:
            return depth_cache[node_id]

        if node_id in input_keys or node_id not in node_ids:
            depth_cache[node_id] = 0
            return 0

        # Prevent pathological cycles by bailing out
        if node_id in stack:
            depth_cache[node_id] = 0
            return depth_cache[node_id]

        incoming = [src for (src, dst) in enabled_connections if dst == node_id]
        if not incoming:
            depth_cache[node_id] = 0
            return 0

        stack.add(node_id)
        depth = 0
        for src in incoming:
            depth = max(depth, resolve_depth(src, stack) + 1)
        stack.discard(node_id)

        depth_cache[node_id] = depth
        return depth

    for node in node_ids:
        resolve_depth(node, set())

    if depth_cache:
        max_depth = max(depth_cache.values())
    else:
        max_depth = 0

    for output in output_keys:
        depth_cache[output] = max_depth

    layers = {}
    for node, depth in depth_cache.items():
        layers.setdefault(depth, []).append(node)

    return layers, enabled_connections


def _node_label(node_id):
    if node_id in INPUT_LABELS:
        return INPUT_LABELS[node_id]
    if node_id in OUTPUT_LABELS:
        return OUTPUT_LABELS[node_id]
    if node_id < 0:
        return f"In {abs(node_id)}"
    if node_id == 0:
        return "Out"
    return f"H{node_id}"


def render_network_diagram(genome, config, width, height):
    """Create a pygame surface with a schematic of the given genome."""
    surface = pygame.Surface((width, height))

    # draw a subtle vertical gradient for depth
    for y in range(height):
        blend = y / max(height - 1, 1)
        shade = int(24 + (40 * blend))
        pygame.draw.line(surface, (shade, shade + 3, shade + 8), (0, y), (width, y))

    if genome is None or config is None:
        text = diagramMessageFont.render("Network unavailable", True, (160, 180, 210))
        surface.blit(text, (10, height // 2 - text.get_height() // 2))
        return surface

    layers, connections = _compute_node_layers(genome, config)
    if not layers:
        text = diagramMessageFont.render("No active topology", True, (160, 180, 210))
        surface.blit(text, (10, height // 2 - text.get_height() // 2))
        return surface

    node_radius = 12
    margin_x = 45
    margin_y = 25
    usable_width = max(width - margin_x * 2, 1)
    layer_keys = sorted(layers.keys())
    layer_count = max(len(layer_keys) - 1, 1)
    column_spacing = usable_width / layer_count if layer_count else 0

    positions = {}
    for index, depth in enumerate(layer_keys):
        nodes = sorted(layers[depth])
        count = len(nodes)
        if count == 1:
            y_positions = [height // 2]
        else:
            usable_height = height - margin_y * 2
            step = usable_height / (count - 1)
            y_positions = [int(margin_y + i * step) for i in range(count)]

        x = int(margin_x + index * column_spacing) if layer_count else width // 2
        for node, y in zip(nodes, y_positions):
            positions[node] = (x, y)

    max_weight = max((abs(conn.weight) for conn in connections.values()), default=1.0)

    for (src, dst), conn in connections.items():
        if src not in positions or dst not in positions:
            continue
        start = positions[src]
        end = positions[dst]
        weight = conn.weight
        norm = min(abs(weight) / max_weight, 1.0)
        thickness = 2 + int(norm * 3)
        color = (90, 220, 150) if weight >= 0 else (235, 105, 105)
        pygame.draw.line(surface, (12, 16, 24), start, end, thickness + 3)
        pygame.draw.line(surface, color, start, end, thickness)

        # annotate weight near the middle of the connection
        mid_x = (start[0] + end[0]) // 2
        mid_y = (start[1] + end[1]) // 2
        weight_text = diagramLabelFont.render(f"{weight:.2f}", True, (210, 215, 235))
        text_rect = weight_text.get_rect(center=(mid_x, mid_y - 12))
        surface.blit(weight_text, text_rect)

    for node, (x, y) in positions.items():
        if node in config.genome_config.input_keys:
            base_color = (120, 170, 250)
        elif node in config.genome_config.output_keys:
            base_color = (250, 200, 110)
        else:
            base_color = (190, 170, 255)

        pygame.draw.circle(surface, (8, 10, 18), (x, y + 2), node_radius + 4)
        pygame.draw.circle(surface, (40, 48, 72), (x, y), node_radius + 3)
        pygame.draw.circle(surface, base_color, (x, y), node_radius)
        pygame.draw.circle(surface, (240, 245, 255), (x, y), node_radius, 1)

        label = _node_label(node)
        text = diagramLabelFont.render(label, True, (230, 235, 250))
        text_rect = text.get_rect(center=(x, y))
        surface.blit(text, text_rect)

    return surface


class Bird:
    IMGs = birdIMGs
    maxRotation = 25
    rotVel = 20
    animationTime = 5
    _id_counter = 1

    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tickCount = 0
        self.vel = 0
        self.height = self.y
        self.imgCount = 0
        self.img = self.IMGs[0]
        self.identifier = Bird._id_counter
        Bird._id_counter += 1
        self.last_action = "Glide"

    def jump(self):
        self.vel = -10.5
        self.tickCount = 0
        self.height = self.y
        self.last_action = "Jump"

    def move(self):
        self.tickCount += 1

        d =  self.vel*self.tickCount + 1.5*self.tickCount**2

        if d >= 16:
            d = 16
        if d < 0:
            d -= 2

        self.y = self.y+d

        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.maxRotation:
                self.tilt = self.maxRotation
            self.last_action = "Climb"
        elif self.tilt > -90:
            self.tilt -= self.rotVel
            self.last_action = "Dive"
        else:
            self.last_action = "Glide"


    def Draw(self,win):
        self.imgCount +=1

        if self.imgCount < self.animationTime:
            self.img = self.IMGs[0]
        elif self.imgCount < self.animationTime * 2:
            self.img = self.IMGs[1]
        elif self.imgCount < self.animationTime * 3:
            self.img = self.IMGs[2]
        elif self.imgCount < self.animationTime * 4:
            self.img = self.IMGs[1]
        elif self.imgCount == self.animationTime * 4 + 1:
            self.img = self.IMGs[0]
            self.imgCount = 0

        if self.tilt <= -80:
            self.img = self.IMGs[1]
            self.imgCount = self.animationTime*2

        rotateImage = pygame.transform.rotate(self.img,self.tilt)
        newReact = rotateImage.get_rect(center= self.img.get_rect(topleft = (self.x,self.y)).center)
        win.blit(rotateImage,newReact.topleft)

    def getMask(self):
        return pygame.mask.from_surface(self.img)

class Pipe:
    gap = 200
    vel = 5

    def __init__(self,x):
        self.x = x
        self.height = 0
        self.gap = 200

        self.top = 0
        self.bottom = 0
        self.pipeTop = pygame.transform.flip(pipeIMG,False,True)
        self.pipeBot = pipeIMG

        self.passed = False
        self.setHeight()

    def setHeight(self):
        self.height = random.randrange(50,450)
        self.top = self.height - self.pipeTop.get_height()
        self.bot = self.height + self.gap

    def move(self):
        self.x -= self.vel

    def draw(self,win):
        win.blit(self.pipeTop, (self.x, self.top))
        win.blit(self.pipeBot, (self.x, self.bot))

    def collide(self,bird):
        birdMask = bird.getMask()
        topMask = pygame.mask.from_surface(self.pipeTop)
        botMask = pygame.mask.from_surface(self.pipeBot)

        topOffset = (self.x - bird.x, self.top - round(bird.y))
        botOffset = (self.x - bird.x, self.bot - round(bird.y))

        bPoint = birdMask.overlap(botMask,botOffset)
        tPoint = birdMask.overlap(topMask,topOffset)

        if tPoint or bPoint:
            return True

        return False

class Base:
    vel = 5
    width = baseIMG.get_width()
    img = baseIMG

    def __init__(self,y):
        self.y = y
        self.x1 = 0
        self.x2 = self.width

    def move(self):
        self.x1 -= self.vel
        self.x2 -= self.vel

        if self.x1 + self.width < 0:
            self.x1 = self.x2 + self.width
        elif self.x2 + self.width < 0:
            self.x2 = self.x1 + self.width

    def draw(self,win):
        win.blit(self.img,(self.x1,self.y))
        win.blit(self.img,(self.x2,self.y))

def drawWindow(win,birds,pipes,base,score,panel_info):
    win.blit(BGIMG,(0,0))
    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)

    for bird in birds:
        bird.Draw(win)

    draw_panel(win, panel_info)

    pygame.display.update()


def draw_panel(win, info):
    """Render the side panel that visualises NEAT training progress."""
    panel_x = WIDTH
    for y in range(HEIGHT):
        blend = y / max(HEIGHT - 1, 1)
        shade = int(18 + blend * 30)
        pygame.draw.line(win, (shade, shade + 4, shade + 12), (panel_x, y), (panel_x + PANEL_WIDTH, y))

    panel_rect = pygame.Rect(panel_x, 0, PANEL_WIDTH, HEIGHT)
    pygame.draw.rect(win, (70, 90, 160), panel_rect, 2)

    y_offset = 20
    title = panelTitleFont.render("Evolution Monitor", True, (220, 235, 255))
    win.blit(title, (panel_x + 20, y_offset))
    y_offset += title.get_height() + 10

    pygame.draw.line(win, (70, 90, 160), (panel_x + 15, y_offset), (panel_x + PANEL_WIDTH - 15, y_offset), 1)
    y_offset += 15

    metrics = [
        f"Generation        {info['generation']}",
        f"Population        {info['population']}",
        f"Alive             {info['alive']}",
        f"Current score     {info['score']}",
        f"Best score        {info['best_score']}",
        f"Best fitness      {info['best_fitness']:.2f}",
        f"Average fitness   {info['avg_fitness']:.2f}",
        f"Score/min         {info['score_rate']:.1f}",
        f"Pipe speed        {info['pipe_speed']:.1f} px/s",
        f"Elapsed           {info['elapsed']:.1f} s",
    ]

    for line in metrics:
        text_surface = panelFont.render(line, True, (210, 220, 250))
        win.blit(text_surface, (panel_x + 20, y_offset))
        y_offset += text_surface.get_height() + 4

    y_offset += 10
    target_title = panelFont.render("Target pipe", True, (160, 190, 255))
    win.blit(target_title, (panel_x + 20, y_offset))
    y_offset += target_title.get_height() + 6

    target_lines = [
        f"X position        {info['target_pipe']['x']:.0f}",
        f"Gap start         {info['target_pipe']['gap_start']:.0f}",
        f"Gap centre        {info['target_pipe']['gap_centre']:.0f}",
        f"Gap end           {info['target_pipe']['gap_end']:.0f}",
    ]

    for line in target_lines:
        target_surface = panelFont.render(line, True, (190, 205, 245))
        win.blit(target_surface, (panel_x + 20, y_offset))
        y_offset += target_surface.get_height() + 2

    y_offset += 10
    network_title = panelFont.render("Network topology", True, (160, 190, 255))
    win.blit(network_title, (panel_x + 20, y_offset))
    y_offset += network_title.get_height() + 6

    diagram_height = 220
    diagram_width = PANEL_WIDTH - 60
    diagram_surface = render_network_diagram(info.get('best_genome'), info.get('config'), diagram_width, diagram_height)
    diagram_pos = (panel_x + 20, y_offset)
    win.blit(diagram_surface, diagram_pos)
    pygame.draw.rect(win, (70, 90, 160), (*diagram_pos, diagram_width, diagram_height), 1)
    y_offset += diagram_height + 8

    y_offset += 10
    section_title = panelFont.render("Top performers", True, (160, 190, 255))
    win.blit(section_title, (panel_x + 20, y_offset))
    y_offset += section_title.get_height() + 6

    if info['top_birds']:
        for entry in info['top_birds']:
            details = (
                f"Bird {entry['id']}  fit {entry['fitness']:.1f}  y {entry['y']:.0f}"
            )
            info_line = panelFont.render(details, True, (200, 210, 240))
            win.blit(info_line, (panel_x + 20, y_offset))
            y_offset += info_line.get_height()

            delta = (
                f"   dx {entry['dx']:.0f}  dy {entry['dy']:.0f}  action {entry['action']}"
            )
            delta_line = panelFont.render(delta, True, (140, 160, 210))
            win.blit(delta_line, (panel_x + 20, y_offset))
            y_offset += delta_line.get_height() + 4
    else:
        info_line = panelFont.render("No birds alive", True, (180, 190, 220))
        win.blit(info_line, (panel_x + 20, y_offset))
        y_offset += info_line.get_height() + 4

    y_offset += 10
    events_title = panelFont.render("Recent events", True, (160, 190, 255))
    win.blit(events_title, (panel_x + 20, y_offset))
    y_offset += events_title.get_height() + 6

    if info['events']:
        for event in reversed(info['events'][-6:]):
            event_surface = panelFont.render(event, True, (150, 170, 215))
            win.blit(event_surface, (panel_x + 20, y_offset))
            y_offset += event_surface.get_height() + 2
    else:
        no_event = panelFont.render("Awaiting data...", True, (150, 170, 215))
        win.blit(no_event, (panel_x + 20, y_offset))

def main(genomes,config):
    global GENERATION, BEST_SCORE, ACTIVE_CONFIG
    GENERATION += 1
    EVENT_LOG.clear()
    ACTIVE_CONFIG = config
    nets = []
    ge = []
    birds = []
    population_size = len(genomes)
    Pipe.vel = 5
    for _,g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g,config)
        nets.append(net)
        birds.append(Bird(230,350))
        g.fitness = 0
        ge.append(g)

    log_event(f"Generation {GENERATION} started with {len(birds)} birds")

    base = Base(730)
    pipes = [Pipe(600)]
    score = 0

    win = ensure_window()
    clock = pygame.time.Clock()
    start_time = time.time()

    final_best_fitness = 0
    run = True
    while run:
        clock.tick(30)
        elapsed = time.time() - start_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit ()
                quit ()

        pipeInd = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].pipeTop.get_width() :
                pipeInd = 1
        else:
            run = False
            break

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1

            output = nets[birds.index(bird)].activate((bird.y, abs(bird.y - pipes[pipeInd].height), abs(bird.y - pipes[pipeInd].bot)))

            if output[0] > 0.5:
                bird.jump()

        rem = []
        addPipe = False
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    crashed_fitness = ge[x].fitness
                    log_event(f"Bird {bird.identifier} crashed | score {score} | fitness {crashed_fitness:.1f}")
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    addPipe = True

            if pipe.x + pipe.pipeTop.get_width() < 0:
                rem.append(pipe)

            pipe.move()

        if addPipe:
            score += 1
            for g in ge:
                g.fitness += 5
            Pipe.vel +=.5
            pipes.append(Pipe(700))
            if score > BEST_SCORE:
                BEST_SCORE = score
                log_event(f"New best score {BEST_SCORE} reached in generation {GENERATION}")
            else:
                log_event(f"Score increased to {score}; pipe speed {Pipe.vel:.1f}")

        for r in rem:
            pipes.remove(r)

        if not pipes:
            pipes.append(Pipe(700))

        pipeInd = max(0, min(pipeInd, len(pipes) - 1))

        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                log_event(f"Bird {bird.identifier} out of bounds at y={bird.y:.0f}")
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        base.move()
        fitness_values = [g.fitness for g in ge]
        best_fitness = max(fitness_values) if fitness_values else 0
        avg_fitness = sum(fitness_values) / len(fitness_values) if fitness_values else 0
        if best_fitness > final_best_fitness:
            final_best_fitness = best_fitness

        target_pipe_info = {"x": 0.0, "gap_start": 0.0, "gap_centre": 0.0, "gap_end": 0.0}
        top_birds = []
        if pipes:
            target_pipe = pipes[pipeInd]
            gap_start = target_pipe.height
            gap_end = target_pipe.bot
            gap_centre = (gap_start + gap_end) / 2
            target_pipe_info = {
                "x": target_pipe.x,
                "gap_start": gap_start,
                "gap_centre": gap_centre,
                "gap_end": gap_end,
            }

            if birds:
                for bird, genome in zip(birds, ge):
                    top_birds.append({
                        "id": bird.identifier,
                        "fitness": genome.fitness,
                        "y": bird.y,
                        "dx": target_pipe.x - bird.x,
                        "dy": gap_centre - bird.y,
                        "action": bird.last_action,
                    })
                top_birds.sort(key=lambda item: item["fitness"], reverse=True)
                top_birds = top_birds[:3]

        score_rate = (score / (elapsed / 60)) if elapsed > 0 else 0

        best_genome = None
        if ge:
            best_index = max(range(len(ge)), key=lambda idx: ge[idx].fitness)
            best_genome = ge[best_index]

        panel_info = {
            "generation": GENERATION,
            "population": population_size,
            "alive": len(birds),
            "score": score,
            "best_score": BEST_SCORE,
            "best_fitness": best_fitness,
            "avg_fitness": avg_fitness,
            "score_rate": score_rate,
            "pipe_speed": Pipe.vel,
            "elapsed": elapsed,
            "target_pipe": target_pipe_info,
            "top_birds": top_birds,
            "events": EVENT_LOG.copy(),
            "best_genome": best_genome,
            "config": ACTIVE_CONFIG,
        }

        drawWindow(win,birds,pipes,base,score,panel_info)

    total_elapsed = time.time() - start_time
    log_event(
        f"Generation {GENERATION} completed | last score {score} | peak fitness {final_best_fitness:.1f} | duration {total_elapsed:.1f}s"
    )


def run(configpath):
    config = neat.config.Config(neat.DefaultGenome,neat.DefaultReproduction,neat.DefaultSpeciesSet,neat.DefaultStagnation,configpath)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main,None)

    return winner


if __name__ == "__main__":
    localDir = os.path.dirname(__file__)
    configPath = os.path.join(localDir,"Config.txt")
    run(configPath)










