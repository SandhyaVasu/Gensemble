#Integrated code - Updated By kaviya 10:50 pm 2nd May
import pygame
import random
import sys
import time
import math
from collections import defaultdict

pygame.init()


# Disable audio in headless mode
os.environ["SDL_AUDIODRIVER"] = "dummy"

try:
    pygame.mixer.init()
except pygame.error:
    print("Audio not available, continuing without sound")

# Screen config
WIDTH, HEIGHT = 1000, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT))
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("GENSEMBLE: The Genome Assembly Game")

# Fonts
font = pygame.font.SysFont("Consolas", 25, bold=True)
small_font = pygame.font.SysFont("Consolas", 20)
FONT = pygame.font.SysFont("Consolas", 18, bold=True)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (100, 100, 255)
GREEN = (0, 200, 0)
PURPLE = (128, 0, 128)
RED = (255, 100, 100)
GRAY = (180, 180, 180)
YELLOW = (255, 255, 0)
PINK = (255, 200, 255)
LIGHT_PINK = (255, 220, 240)
MEDIUM_PURPLE = (147, 112, 219)
LIGHT_PURPLE = (204, 153, 255)
YELLOW_NODE = (255, 255, 0)

# Node and button sizes
NODE_RADIUS = 40
RESET_BUTTON_SIZE = (120, 40)
BACK_BUTTON_RECT = pygame.Rect(20, HEIGHT - 60, 100, 40)

import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller sets this
    except AttributeError:
        base_path = os.path.abspath(".")  # fallback when running normally
    return os.path.join(base_path, relative_path)


# Load sounds
try:
    click_sound = pygame.mixer.Sound(resource_path("pop.mp3"))
    correct_sound = pygame.mixer.Sound(resource_path("correct.mp3"))
    wrong_sound = pygame.mixer.Sound(resource_path("wrong.mp3"))
    happy_sound = pygame.mixer.Sound(resource_path("happy.wav"))
    very_happy_sound = pygame.mixer.Sound(resource_path("very_happy.wav"))
    victory_sound = pygame.mixer.Sound(resource_path("happy.wav"))
    failure_sound = pygame.mixer.Sound(resource_path("pop.mp3"))

except pygame.error as e:
    print(f"Could not load sound file: {e}")
    class DummySound:
        def play(self):
            pass
    click_sound = correct_sound = wrong_sound = happy_sound = very_happy_sound = victory_sound = failure_sound = DummySound()


# Fragment sets per level (Overlap Game)
level_fragments_overlap = {
    "Beginner": ["ATTGC", "TTGCT", "TGCTA", "GCTAG", "CTAGG", "TAGGC", "AGGCC", "GGCCT", "GCCTA"],
    "Intermediate": ["ATGCC", "TGCCA", "GCCAT", "CCATT", "CATTT", "ATTTG", "TTTGC", "TTGCG", "TGCGG"],
    "Pro": ["AACGT", "ACGTT", "CGTTC", "GTTCG", "TTCGA", "TCGAA", "CGAAC", "GAACC", "AACCT"]
}

# Difficulty config (Hamiltonian Path Game)
easy_k_mers = ["ATTGC", "TTGCT", "TGCTA", "GCTAG", "CTAGG", "TAGGC", "AGGCC", "GGCCT", "GCCTA"]
hard_dna = "TAATGCCATGGGATGTT"
hard_k = 4

# De Bruijn Game Data
dna_sequences = {
    "beginner": ("ATTGCTAGGCCTA", 5),
    "intermediate": ("TAATGCCATGGGATGTT", 4),
    "pro": ("AGCTAGGCTAGCTAGGCTACGTAGCTAGCTAGTCA", 6)
}

level_timer = {
    "beginner": None,
    "intermediate": 90,
    "pro": 60
}

hamiltonian_timer = {
    "easy": None,
    "moderate": 90,
    "difficult": 60
}

click_limits = {
    "beginner": 30,
    "intermediate": 25,
    "pro": 20
}

# Game state
game_state = "menu"  # could be 'menu', 'overlap', 'hamiltonian', 'debruijn'
current_level = None
assembled_fragments = []
score = 0
submitted = False
resets_left = 5
show_fun_fact = False
sound_played = False
show_game_over = False
fragments = []
fragment_positions = []
fragment_rects = []
total_moves = 12
start_time = None
time_limit = None
game_over_message = ""

# Hamiltonian Path Game state
nodes_hamiltonian = []
graph_hamiltonian = defaultdict(list)
positions_hamiltonian = {}
selected_path_hamiltonian = []
visited_hamiltonian = set()
game_over_hamiltonian = False
success_hamiltonian = False
reset_count_hamiltonian = 5
error_msg_hamiltonian = ""
reset_flag_hamiltonian = False
show_intro_hamiltonian = False
difficulty_selected = False
allow_fuzzy = False
victory_played = False


#Rectangles
reset_button_rect = pygame.Rect(WIDTH - 150, 80, 100, 40)
info_icon_rect = pygame.Rect(WIDTH - 50, HEIGHT // 2 - 20, 30, 30)
fun_fact_rect = pygame.Rect(WIDTH - 330, HEIGHT // 2 - 90, 300, 180)
close_button_rect = pygame.Rect(fun_fact_rect.right - 25, fun_fact_rect.top + 5, 20, 20)
ok_button_rect = pygame.Rect(WIDTH // 2 - 50, HEIGHT // 2 + 50, 100, 40)
back_button_rect = pygame.Rect(20, 20, 100, 40)
menu_button_rect = pygame.Rect(WIDTH // 2 - 60, HEIGHT - 80, 120, 40) # For Hamiltonian back to menu
reset_button_rect_hamiltonian = pygame.Rect(WIDTH - 150, 80, 100, 40)


fun_fact_text = [
    "Fun Fact!",
    " ",
    "DNA bases are often",
    "coloured",
    "A - Blue, T - Yellow,",
    "G - Green, C - Red.",
    "This convention is used",
    "by many biologists and",
    "bioinformatics tools!"
]

# Error simulation for Hamiltonian Game
def introduce_errors(kmers, error_rate=0.2):
    bases = ["A", "T", "C", "G"]
    mutated = []
    for kmer in kmers:
        kmer_list = list(kmer)
        for i in range(len(kmer_list)):
            if random.random() < error_rate:
                original = kmer_list[i]
                kmer_list[i] = random.choice([b for b in bases if b != original])
        mutated.append("".join(kmer_list))
    return mutated

def fuzzy_match(k1, k2, max_mismatch=2):
    return sum(a != b for a, b in zip(k1, k2)) <= max_mismatch

def build_graph(kmer_nodes, fuzzy=False):
    graph = defaultdict(list)
    for i, (id1, k1) in enumerate(kmer_nodes):
        suffix = k1[1:]
        for j, (id2, k2) in enumerate(kmer_nodes):
            if i != j:
                prefix = k2[:-1]
                if (fuzzy and fuzzy_match(suffix, prefix)) or (not fuzzy and suffix == prefix):
                    graph[id1].append(id2)
    return graph

def generate_node_positions(node_ids, width, height, node_radius):
    positions = {}
    margin = node_radius * 2 + 20
    attempts = 100
    for node_id in node_ids:
        placed = False
        for _ in range(attempts):
            x = random.randint(margin, width - margin)
            y = random.randint(margin, height - margin)
            if all((x - ox) ** 2 + (y - oy) ** 2 >= (node_radius * 2) ** 2 for ox, oy in positions.values()):
                positions[node_id] = (x, y)
                placed = True
                break
        if not placed:
            print(f"Warning: Could not place node {node_id} without overlap.")
    return positions

def draw_arrow(surface, start, end, color=BLACK, width=2, arrow_size=10):
    pygame.draw.line(surface, color, start, end, width)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    dx, dy = math.cos(angle), math.sin(angle)
    left = (end[0] - arrow_size * (dx + dy / 2), end[1] - arrow_size * (dy - dx / 2))
    right = (end[0] - arrow_size * (dx - dy / 2), end[1] - arrow_size * (dy + dx / 2))
    pygame.draw.polygon(surface, color, [end, left, right])

def draw_kmer_text(kmer, x, y, font_to_use=FONT):
    spacing = font_to_use.size("A")[0] + 2
    text_width = spacing * len(kmer)
    start_x = x - text_width // 2
    for i, base in enumerate(kmer):
        color = {"A": BLUE, "C": RED, "G": GREEN, "T": YELLOW}.get(base, WHITE)
        bx = start_x + i * spacing
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if dx or dy:
                    shadow = font_to_use.render(base, True, BLACK)
                    screen.blit(shadow, (bx + dx, y + dy))
        text = font_to_use.render(base, True, color)
        screen.blit(text, (bx, y))


def draw_reset_button(reset_count, button_rect, surface):
    pygame.draw.rect(surface, LIGHT_PURPLE, button_rect, border_radius=12)
    pygame.draw.rect(surface, BLACK, button_rect, 3, border_radius=12)
    reset_text = FONT.render(f"Reset ({reset_count})", True, BLACK)
    surface.blit(reset_text, (button_rect.x + (button_rect.width - reset_text.get_width()) // 2,
                             button_rect.y + (button_rect.height - reset_text.get_height()) // 2))
    return button_rect

def reset_game_overlap(first_time=False):
    global fragments, assembled_fragments, score, submitted, fragment_positions, fragment_rects
    global sound_played, total_moves, show_game_over, start_time, resets_left, game_over_message

    if not first_time:
        if resets_left <= 0:
            return
        resets_left = max(resets_left - 1, 0)

    fragments = level_fragments_overlap[current_level][:]
    random.shuffle(fragments)
    assembled_fragments.clear()
    score = 0
    submitted = False
    sound_played = False
    show_game_over = False
    game_over_message = ""
    total_moves = 12
    fragment_positions.clear()
    fragment_rects.clear()

    if time_limit is not None:
        start_time = time.time()

    for i in range(len(fragments)):
        row = i // 5
        col = i % 5
        x = 100 + col * 130
        y = 400 + row * 70
        fragment_positions.append((x, y))

    for i, fragment in enumerate(fragments):
        # Simplified rect creation
        text_width = font.size(fragment)[0]
        rect = pygame.Rect(fragment_positions[i][0], fragment_positions[i][1], text_width + 10, 40)
        fragment_rects.append(rect)

def draw_reset_button(resets_left, reset_button_rect, screen):
    font = pygame.font.SysFont(None, 32)
    WHITE = (255, 255, 255)
    pygame.draw.rect(screen, PURPLE, reset_button_rect)
    pygame.draw.rect(screen, BLACK, reset_button_rect, 2)
    button_text = font.render(f"Reset ({resets_left})", True, WHITE)
    text_rect = button_text.get_rect(center=reset_button_rect.center)
    screen.blit(button_text, text_rect)
    return reset_button_rect

def is_valid_addition(new_fragment):
    if not assembled_fragments:
        return True
    return assembled_fragments[-1][-4:] == new_fragment[:4]

def get_aligned_fragments_pixelwise():
    if not assembled_fragments:
        return []
    aligned_data = []
    x_pos = 50
    y_pos = 150
    char_spacing = font.size("A")[0] - 2
    for i, fragment in enumerate(assembled_fragments):
        aligned_data.append((fragment, x_pos, y_pos))
        if i < len(assembled_fragments) - 1:
            x_pos += (len(fragment) - 4) * char_spacing + 2
        y_pos += font.get_linesize()
    return aligned_data

def draw_back_button(surface):
    pygame.draw.rect(surface, LIGHT_PURPLE, BACK_BUTTON_RECT, border_radius=8)
    pygame.draw.rect(surface, BLACK, BACK_BUTTON_RECT, 2, border_radius=8)
    text = FONT.render("Back", True, BLACK)
    surface.blit(text, (BACK_BUTTON_RECT.x + 20, BACK_BUTTON_RECT.y + 10))
    return BACK_BUTTON_RECT

def draw_level_menu():
    screen.fill(MEDIUM_PURPLE)

    # Main title
    title_main_font = pygame.font.SysFont(None, 40)
    title_main = title_main_font.render("Gensemble: The Genome Assembly Game", True, WHITE)
    screen.blit(title_main, (WIDTH // 2 - title_main.get_width() // 2, 40))
    # Section title
    title = font.render("Select Level", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))
    start_y = 160
    button_width = 300
    button_height = 50
    spacing = 60
    max_font_size = 28
    # Define three distinct colors
    color_group_1 = (255, 204, 204)   # Light pink
    color_group_2 = (204, 229, 255)   # Light blue
    color_group_3 = (204, 255, 204)   # Light green
    buttons = []
    button_data = [
        ("Overlap - Beginner", "overlap", "Beginner"),
        ("Overlap - Intermediate", "overlap", "Intermediate"),
        ("Overlap - Pro", "overlap", "Pro"),
        ("Hamiltonian - Beginner", "hamiltonian", "easy"),
        ("Hamiltonian - Intermediate", "hamiltonian", "moderate"),
        ("Hamiltonian - Pro", "hamiltonian", "difficult"),
        ("De Bruijn - Beginner", "debruijn", "beginner"),
        ("De Bruijn - Intermediate", "debruijn", "intermediate"),
        ("De Bruijn - Pro", "debruijn", "pro")
    ]

    for i, (name, game, level) in enumerate(button_data):
        rect = pygame.Rect(WIDTH // 2 - button_width // 2, start_y + i * spacing, button_width, button_height)
        buttons.append((name, rect, game, level))

        # Assign color based on group
        if i < 3:
            fill_color = color_group_3
        elif i < 6:
            fill_color = color_group_2
        else:
            fill_color = color_group_1

        pygame.draw.rect(screen, fill_color, rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, rect, 2, border_radius=10)
        current_font_size = max_font_size
        while True:
            temp_font = pygame.font.SysFont(None, current_font_size)
            label = temp_font.render(name, True, BLACK)
            if label.get_width() <= button_width - 20 or current_font_size <= 12:
                break
            current_font_size -= 1

        screen.blit(label, (rect.centerx - label.get_width() // 2, rect.centery - label.get_height() // 2))

    return buttons

# Hamiltonian Game functions
def reset_game_hamiltonian(show_msg=True):
    global selected_path_hamiltonian, visited_hamiltonian, game_over_hamiltonian, success_hamiltonian, reset_count_hamiltonian, error_msg_hamiltonian, reset_flag_hamiltonian, victory_played
    selected_path_hamiltonian = []
    visited_hamiltonian = set()
    game_over_hamiltonian = False
    success_hamiltonian = False
    victory_played = False
    reset_flag_hamiltonian = True
    reset_count_hamiltonian -= 1
    if reset_count_hamiltonian <= 0:
        reset_count_hamiltonian = 0
        game_over_hamiltonian = True
        error_msg_hamiltonian = "Oops! try again"
        failure_sound.play()
    elif show_msg:
        error_msg_hamiltonian = "Resetted. Try again"

def get_gene_sequence_from_path(path, nodes):
    if not path:
        return ""
    sequence = nodes[path[0]][1]
    for i in range(1, len(path)):
        sequence += nodes[path[i]][1][-1]
    return sequence

def generate_kmers_from_sequence(seq, k):
    return [seq[i:i+k] for i in range(len(seq) - k + 1)]

def init_game_hamiltonian(difficulty):
    global nodes_hamiltonian, graph_hamiltonian, positions_hamiltonian, show_intro_hamiltonian, reset_count_hamiltonian, allow_fuzzy
    reset_count_hamiltonian = 5
    show_intro_hamiltonian = True
    allow_fuzzy = False

    if difficulty == "easy":
        kmers = easy_k_mers
    elif difficulty == "moderate":
        kmers = generate_kmers_from_sequence(hard_dna, hard_k)
    elif difficulty == "difficult":
        allow_fuzzy = True
        kmers = introduce_errors(easy_k_mers, error_rate=0.2)

    nodes_hamiltonian = [(i, k) for i, k in enumerate(kmers)]
    graph_hamiltonian = build_graph(nodes_hamiltonian, fuzzy=allow_fuzzy)
    random.shuffle(nodes_hamiltonian)
    return generate_node_positions([node[0] for node in nodes_hamiltonian], WIDTH, HEIGHT, NODE_RADIUS)

def show_instruction_screen_hamiltonian():
    instruction_running = True
    font = pygame.font.SysFont(None, 32)
    big_font = pygame.font.SysFont(None, 48)

    instructions = [
        "Welcome to the Hamiltonian Path Level!",
        "Instructions:",
        "- In this level, DNA reads (k-mers) are represented as nodes in a graph.",
        "- An edge from one node to another means the suffix of one k-mer",
        "  overlaps with the prefix of another.",
        "- Your task is to find a path that visits each node exactly once.",
        "This is called a Hamiltonian Path!",
        "- Click nodes in order to build your path.",
        "- You have limited resets, and in higher levels, errors or fuzziness are introduced.",
        "",
        "Hit Start to begin your challenge!"
    ]

    button_width = 200
    button_height = 50
    button_x = (WIDTH - button_width) // 2
    button_y = HEIGHT - 100
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

    while instruction_running:
        screen.fill(MEDIUM_PURPLE)
        instruction_box = pygame.Rect(40, 40, WIDTH - 60, 400)
        pygame.draw.rect(screen, LIGHT_PINK, instruction_box, border_radius=15)
        pygame.draw.rect(screen, BLACK, instruction_box, 3, border_radius=15)

        for i, line in enumerate(instructions):
            text = font.render(line, True, BLACK)
            screen.blit(text, (60, 60 + i * 35))

        pygame.draw.rect(screen, PURPLE, button_rect)
        pygame.draw.rect(screen, BLACK, button_rect, 2)
        button_text = font.render("Start", True, WHITE)
        text_rect = button_text.get_rect(center=button_rect.center)
        screen.blit(button_text, text_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    instruction_running = False

def game_loop_hamiltonian(level):
    global game_over_hamiltonian, success_hamiltonian, show_intro_hamiltonian, error_msg_hamiltonian, reset_flag_hamiltonian, victory_played, reset_count_hamiltonian
    show_instruction_screen_hamiltonian()
    clock = pygame.time.Clock()
    running = True
    positions_hamiltonian = init_game_hamiltonian(level)

    while running:
        screen.fill(MEDIUM_PURPLE)
        draw_back_button(screen)

        for src_id in graph_hamiltonian:
            x1, y1 = positions_hamiltonian[src_id]
            for dst_id in graph_hamiltonian[src_id]:
                x2, y2 = positions_hamiltonian[dst_id]
                angle = math.atan2(y2 - y1, x2 - x1)
                offset_src = (x1 + NODE_RADIUS * math.cos(angle), y1 + NODE_RADIUS * math.sin(angle))
                offset_dst = (x2 - NODE_RADIUS * math.cos(angle), y2 - NODE_RADIUS * math.sin(angle))
                draw_arrow(screen, offset_src, offset_dst)

        for node_id, kmer in nodes_hamiltonian:
            x, y = positions_hamiltonian[node_id]
            color = YELLOW_NODE if node_id in selected_path_hamiltonian else PINK
            pygame.draw.circle(screen, color, (int(x), int(y)), NODE_RADIUS)
            pygame.draw.circle(screen, BLACK, (int(x), int(y)), NODE_RADIUS, 2)
            draw_kmer_text(kmer, x, y)

        score_text = FONT.render(f"Score: {len(selected_path_hamiltonian)} / {len(nodes_hamiltonian)}", True, BLACK)
        screen.blit(score_text, (20, 20))

        if selected_path_hamiltonian:
            partial_seq = get_gene_sequence_from_path(selected_path_hamiltonian, nodes_hamiltonian)
            seq_text = FONT.render(f"Current sequence: {partial_seq}", True, BLACK)
            screen.blit(seq_text, (20, 50))


        if game_over_hamiltonian:
            popup = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 75, 400, 150)
            pygame.draw.rect(screen, LIGHT_PINK, popup, border_radius=15)
            pygame.draw.rect(screen, BLACK, popup, 3, border_radius=15)
            fail_msg = FONT.render(error_msg_hamiltonian or "Oops! Try again.", True, BLACK)
            screen.blit(fail_msg, (popup.centerx - fail_msg.get_width() // 2, popup.centery - fail_msg.get_height() // 2))

        if success_hamiltonian:
            if not victory_played:
                victory_sound.play()
                victory_played = True
            popup = pygame.Rect(WIDTH // 2 - 250, HEIGHT // 2 - 100, 500, 200)
            pygame.draw.rect(screen, LIGHT_PINK, popup, border_radius=15)
            pygame.draw.rect(screen, BLACK, popup, 3, border_radius=15)
            success_msg = FONT.render("✅ Hurray! You found the Hamiltonian path!", True, BLACK)
            screen.blit(success_msg, (popup.centerx - success_msg.get_width() // 2, popup.y + 30))
            full_sequence = get_gene_sequence_from_path(selected_path_hamiltonian, nodes_hamiltonian)
            lines = [full_sequence[i:i+70] for i in range(0, len(full_sequence), 70)]
            for i, line in enumerate(lines):
                line_render = FONT.render(line, True, BLACK)
                screen.blit(line_render, (popup.centerx - line_render.get_width() // 2, popup.y + 70 + i * 20))

        reset_button = draw_reset_button(reset_count_hamiltonian, reset_button_rect_hamiltonian, screen)
        menu_button = pygame.Rect(WIDTH // 2 - 60, HEIGHT - 80, 120, 40)
        pygame.draw.rect(screen, LIGHT_PURPLE, menu_button, border_radius=10)
        pygame.draw.rect(screen, BLACK, menu_button, 2, border_radius=10)
        menu_text = FONT.render("Back to Menu", True, BLACK)
        screen.blit(menu_text, (menu_button.centerx - menu_text.get_width() // 2,
                                 menu_button.centery - menu_text.get_height() // 2))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if reset_button.collidepoint(mx, my) and reset_count_hamiltonian >0:
                    reset_game_hamiltonian()
                elif menu_button.collidepoint(mx, my):
                    return
                elif BACK_BUTTON_RECT.collidepoint(mx, my):
                    return
                if not success_hamiltonian and not game_over_hamiltonian:
                    for node_id, kmer in nodes_hamiltonian:
                        x, y = positions_hamiltonian[node_id]
                        if (mx - x) ** 2 + (my - y) ** 2 <= NODE_RADIUS ** 2:
                            if reset_flag_hamiltonian:
                                reset_flag_hamiltonian = False
                                error_msg_hamiltonian = ""
                            if not selected_path_hamiltonian:
                                selected_path_hamiltonian.append(node_id)
                                visited_hamiltonian.add(node_id)
                                error_msg_hamiltonian = ""
                                correct_sound.play()
                            else:
                                last_id = selected_path_hamiltonian[-1]
                                if node_id not in visited_hamiltonian and node_id in graph_hamiltonian[last_id]:
                                    selected_path_hamiltonian.append(node_id)
                                    visited_hamiltonian.add(node_id)
                                    error_msg_hamiltonian = ""
                                    correct_sound.play()
                                elif node_id not in graph_hamiltonian[last_id]:
                                    error_msg_hamiltonian = "Invalid node. Must overlap with previous."
                                    wrong_sound.play()
                                else:
                                    reset_game_hamiltonian(True)
                                    wrong_sound.play()
                            break
                    if len(selected_path_hamiltonian) == len(nodes_hamiltonian):
                        success_hamiltonian = True
                    elif selected_path_hamiltonian:
                        last_id = selected_path_hamiltonian[-1]
                        if not any(n not in visited_hamiltonian for n in graph_hamiltonian[last_id]):
                            reset_game_hamiltonian()
                            failure_sound.play()
        pygame.display.flip()
        clock.tick(60)
    clear_hamiltonian_state()
    return
def clear_hamiltonian_state():
    global selected_path_hamiltonian, visited_hamiltonian, game_over_hamiltonian
    global success_hamiltonian, error_msg_hamiltonian, reset_flag_hamiltonian
    global show_intro_hamiltonian, victory_played

    selected_path_hamiltonian = []
    visited_hamiltonian = set()
    game_over_hamiltonian = False
    success_hamiltonian = False
    error_msg_hamiltonian = ""
    reset_flag_hamiltonian = False
    show_intro_hamiltonian = False
    victory_played = False


# De Bruijn Game functions
def generate_de_bruijn_graph(seq, k):
    graph = defaultdict(list)
    edges = []
    for i in range(len(seq) - k + 1):
        kmer = seq[i:i + k]
        prefix = kmer[:-1]
        suffix = kmer[1:]
        edge_id = f"{prefix}->{suffix}_{i}"
        graph[prefix].append((suffix, kmer, edge_id))  # Creating the graph's edges
        edges.append((prefix, suffix, kmer, edge_id))  # Storing edges for later use
    print("Generated Graph Edges:")
    for node, edge_list in graph.items():
        print(f"{node}: {edge_list}")
    return graph, edges
def generate_node_positions_debruijn(nodes):
    positions = {}
    angle_step = 2 * math.pi / len(nodes)
    radius = min(WIDTH, HEIGHT) // 2.5
    center_x, center_y = WIDTH // 2, HEIGHT // 2
    for i, node in enumerate(nodes):
        angle = i * angle_step
        x = int(center_x + radius * math.cos(angle))
        y = int(center_y + radius * math.sin(angle))
        positions[node] = (x, y)
    return positions

def draw_kmer_text_debruijn(kmer, x, y):
    spacing = FONT.size("A")[0] + 2
    for i, base in enumerate(kmer):
        color = {"A": BLUE, "C": RED, "G": GREEN, "T": YELLOW}.get(base, WHITE)
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if dx or dy:
                    shadow = FONT.render(base, True, BLACK)
                    screen.blit(shadow, (x + i * spacing + dx, y + dy))
        text = FONT.render(base, True, color)
        screen.blit(text, (x + i * spacing, y))

def draw_arrow_debruijn(surface, start, end, color=BLACK, width=2, arrow_size=10, offset=(0, 0)):
    start = (start[0] + offset[0], start[1] + offset[1])
    end = (end[0] + offset[0], end[1] + offset[1])

    dx, dy = end[0] - start[0], end[1] - start[1]
    distance = math.hypot(dx, dy)

    if distance == 0:
        return
    ux, uy = dx / distance, dy / distance
    shaft_start = (start[0] + ux * NODE_RADIUS, start[1] + uy * NODE_RADIUS)
    shaft_end = (end[0] - ux * (NODE_RADIUS + arrow_size + 2), end[1] - uy * (NODE_RADIUS + arrow_size + 2))
    pygame.draw.line(surface, color, shaft_start, shaft_end, width)
    tip = (end[0] - ux * NODE_RADIUS, end[1] - uy *(NODE_RADIUS +5) )
    left = (
        tip[0] - arrow_size * math.cos(math.atan2(dy, dx) - math.pi / 6),
        tip[1] - arrow_size * math.sin(math.atan2(dy, dx) - math.pi / 6),
    )
    right = (
        tip[0] - arrow_size * math.cos(math.atan2(dy, dx) + math.pi / 6),
        tip[1] - arrow_size * math.sin(math.atan2(dy, dx) + math.pi / 6),
    )
    pygame.draw.polygon(surface, color, [tip, left, right])

def draw_pointer_debruijn(surface, position):
    x, y = position
    pygame.draw.polygon(surface, PURPLE, [(x, y - NODE_RADIUS - 10), (x - 10, y - NODE_RADIUS - 30), (x + 10, y - NODE_RADIUS - 30)])

def show_instruction_debruijn():
    instruction_running = True
    font = pygame.font.SysFont(None, 32)
    big_font = pygame.font.SysFont(None, 48)

    instructions = [
        "Welcome to the De Bruijjn Level!",
        "Instructions:",
        "In this level, we will explore genome reconstruction using a De Bruijn graph.",
        "What is a De Bruijn graph?",
        "Imagine you have these DNA fragments (called k-mers). We build a graph where:",
        "1) Each node is a string of length (k-1) — in this case,",
        "2-letter combinations like AT, TG, GA.",
        "2) Each edge connects one node to another, based on a fragment.",
        "For example, if the fragments are: ATG, TGA, GAT, ATC. For ATG",
        "Start node: AT (first 2 letters)",
        "End node: TG (last 2 letters)",
        "So we draw an arrow from AT -> TG",
        "This is done for all fragments.",
        "What is an Eulerian Path?",
        "An Eulerian path is a trail in a graph that visits every edge exactly once.",
        "In this level, your task is to find the Eulerian path in the De Bruijn graph.",
        "Hit start to begin..."
    ]

    button_width = 200
    button_height = 50
    button_x = button_width+500
    button_y = button_height+500
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    while instruction_running:
        screen.fill(MEDIUM_PURPLE)
        instruction_box = pygame.Rect(40, 30, WIDTH - 80, 700)
        pygame.draw.rect(screen, LIGHT_PINK, instruction_box, border_radius=15)
        pygame.draw.rect(screen, BLACK, instruction_box, 3, border_radius=15)
        for i, line in enumerate(instructions):
            text = font.render(line, True, BLACK)
            screen.blit(text, (50, 50 + i * 40))
        font = pygame.font.SysFont(None, 32)
        WHITE = (255, 255, 255)
        pygame.draw.rect(screen, PURPLE, button_rect)
        pygame.draw.rect(screen, BLACK, button_rect, 2)
        button_text = font.render("Start", True, WHITE)
        text_rect = button_text.get_rect(center=button_rect.center)
        screen.blit(button_text, text_rect)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if button_rect.collidepoint(mx, my):
                    instruction_running = False

def game_loop_debruijn(level):
    show_instruction_debruijn()
    resets_left_debruijn = 5
    show_game_over = False
    game_over_message = ""
    final_score = None  # Store final score here
    sequence, k = dna_sequences[level]
    timer_duration = level_timer[level]
    max_clicks = click_limits[level]

    graph, edges = generate_de_bruijn_graph(sequence, k)
    nodes = list(set([u for u, v, _, _ in edges] + [v for u, v, _, _ in edges]))
    positions = generate_node_positions_debruijn(nodes)
    used_edge_ids = set()
    path = []
    selected_node = None

    start_time = time.time()
    click_count = 0
    assembled = ""

    running = True
    clock = pygame.time.Clock()
    while running:
        screen.fill(MEDIUM_PURPLE)
        draw_back_button(screen)

        if timer_duration:
            time_left = max(0, int(timer_duration - (time.time() - start_time)))
            timer_text = FONT.render(f"Time Left: {time_left}s", True, BLACK)
            screen.blit(timer_text, (WIDTH - 200, 20))
            if time_left <= 0 and not show_game_over:
                failure_sound.play()
                assembled_genome = path[0] + ''.join(n[-1] for n in path[1:]) if path else ""
                final_score = len(path)
                game_over_message = f"⏰ Time's up! Partial Assembly: {assembled_genome}"
                show_game_over = True

        click_text = FONT.render(f"Clicks Left: {max(0, max_clicks - click_count)}", True, BLACK)
        screen.blit(click_text, (WIDTH - 200, 50))
        score_text = FONT.render(f"Score: {len(path)}", True, BLACK)
        screen.blit(score_text, (20, 20))
        reset_button_rect = draw_reset_button(resets_left_debruijn, pygame.Rect(WIDTH - 150, 80, 100, 40), screen)

        edge_draw_offsets = defaultdict(int)
        for u, v, label, edge_id in edges:
            color = GREEN if edge_id in used_edge_ids else BLACK
            offset_index = edge_draw_offsets[(u, v)]
            angle_offset = math.pi / 18 * offset_index
            offset_dx = int(10 * math.cos(angle_offset))
            offset_dy = int(10 * math.sin(angle_offset))
            offset = (offset_dx, offset_dy)
            edge_draw_offsets[(u, v)] += 1
            draw_arrow_debruijn(screen,
                (positions[u][0] + offset[0], positions[u][1] + offset[1]),
                (positions[v][0] + offset[0], positions[v][1] + offset[1]),
                color=color
            )

        for node in nodes:
            x, y = positions[node]
            pygame.draw.circle(screen, YELLOW_NODE if node in path else PINK, (x, y), NODE_RADIUS)
            pygame.draw.circle(screen, BLACK, (x, y), NODE_RADIUS, 2)
            draw_kmer_text_debruijn(node, x - NODE_RADIUS + 12, y - 10)

        if selected_node:
            draw_pointer_debruijn(screen, positions[selected_node])

        if show_game_over:
            popup = pygame.Rect(WIDTH // 2 - 220, HEIGHT // 2 - 120, 440, 220)
            pygame.draw.rect(screen, LIGHT_PINK, popup, border_radius=15)
            pygame.draw.rect(screen, BLACK, popup, 3, border_radius=15)

            msg1 = FONT.render(game_over_message, True, BLACK)
            screen.blit(msg1, (popup.centerx - msg1.get_width() // 2, popup.y + 40))

            if final_score is not None:
                score_msg = FONT.render(f"Score: {final_score}", True, BLACK)
                screen.blit(score_msg, (popup.centerx - score_msg.get_width() // 2, popup.y + 90))

            pygame.draw.rect(screen, LIGHT_PURPLE, ok_button_rect, border_radius=8)
            pygame.draw.rect(screen, BLACK, ok_button_rect, 2, border_radius=8)
            ok_text = FONT.render("OK", True, BLACK)
            screen.blit(ok_text, (ok_button_rect.centerx - ok_text.get_width() // 2, ok_button_rect.centery - ok_text.get_height() // 2))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if BACK_BUTTON_RECT.collidepoint(mx, my):
                    return
                elif show_game_over and ok_button_rect.collidepoint(mx, my):
                    return
                elif 'reset_button_rect' in locals() and reset_button_rect.collidepoint(mx, my) and not show_game_over and resets_left_debruijn > 0:
                    graph, edges = generate_de_bruijn_graph(sequence, k)
                    nodes = list(set([u for u, v, _, _ in edges] + [v for u, v, _, _ in edges]))
                    positions = generate_node_positions_debruijn(nodes)
                    used_edge_ids.clear()
                    path.clear()
                    selected_node = None
                    assembled = ""
                    click_count = 0
                    start_time = time.time()
                    resets_left_debruijn -= 1
                    correct_sound.play()
                for node in nodes:
                    x, y = positions[node]
                    if (mx - x)**2 + (my - y)**2 <= NODE_RADIUS**2:
                        if click_count >= max_clicks:
                            continue
                        if selected_node is None:
                            selected_node = node
                            path.append(node)
                            click_count += 1
                            continue
                        found_edge = None
                        for edge in edges:
                            u, v, label, edge_id = edge
                            if u == selected_node and v == node and edge_id not in used_edge_ids:
                                found_edge = edge
                                break
                        if found_edge:
                            _, _, label, edge_id = found_edge
                            if edge_id not in used_edge_ids:
                                used_edge_ids.add(edge_id)
                                assembled += selected_node[-1]
                                correct_sound.play()
                            selected_node = node
                            path.append(node)
                            click_count += 1
                        else:
                            wrong_sound.play()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and not show_game_over:
                assembled_genome = path[0] + ''.join(n[-1] for n in path[1:]) if path else ""
                final_score = len(path)
                game_over_message = f"✅ Genome Assembled: {assembled_genome}"
                victory_sound.play()
                show_game_over = True

        clock.tick(60)

    pygame.quit()
    sys.exit()

def show_instruction_screen_overlap():
    instruction_running = True
    font = pygame.font.SysFont(None, 32)
    big_font = pygame.font.SysFont(None, 48)

    instructions = [
        "Welcome to the Overlap Assembly Level!",
        "Instructions:",
        "- On the screen, you will see fragments of DNA.",
        "— Each fragment is a short sequence of nucleotides of length k called k-mers.",
        "- Your task is to assemble them into a complete sequence.",
        " The fragments are 5-mers with overlaps of 4-mers",
        "- Only valid overlaps will be accepted, that is,",
        "the last four of one fragment must be the same as first four of the next",
        "- You lose a move for every incorrect placement.",
        "- You have a timer for intermediate and pro levels!",
        "",
        "Hit start to begin..."
    ]

    button_width = 200
    button_height = 50
    button_x = (WIDTH - button_width) // 2
    button_y = HEIGHT - 100
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    while instruction_running:
        screen.fill(MEDIUM_PURPLE)
        instruction_box = pygame.Rect(40, 40, WIDTH - 80, 500)
        pygame.draw.rect(screen, LIGHT_PINK, instruction_box, border_radius=15)
        pygame.draw.rect(screen, BLACK, instruction_box, 3, border_radius=15)
        for i, line in enumerate(instructions):
            text = font.render(line, True, BLACK)
            screen.blit(text, (50, 50 + i * 40))
        font = pygame.font.SysFont(None, 32)
        WHITE = (255, 255, 255)
        pygame.draw.rect(screen, PURPLE, button_rect)
        pygame.draw.rect(screen, BLACK, button_rect, 2)
        button_text = font.render("Start", True, WHITE)
        text_rect = button_text.get_rect(center=button_rect.center)
        screen.blit(button_text, text_rect)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if button_rect.collidepoint(mx, my):
                    instruction_running = False

def game_loop_overlap(level):
    global assembled_fragments, fragments, score, submitted, show_game_over, start_time, time_limit, resets_left, total_moves, fragment_rects, fragment_positions, show_fun_fact, sound_played, current_level, game_over_message

    current_level = level
    resets_left = 5
    reset_game_overlap(first_time=True)

    running = True
    clock = pygame.time.Clock()

    while running:
        screen.fill(MEDIUM_PURPLE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if not show_game_over and not show_fun_fact:
                    for i, rect in enumerate(fragment_rects):
                        if rect.collidepoint(mx, my):
                            selected_fragment = fragments[i]
                            if is_valid_addition(selected_fragment):
                                assembled_fragments.append(selected_fragment)
                                fragments.pop(i)
                                fragment_rects.pop(i)
                                fragment_positions.pop(i)
                                score += 1
                                total_moves -= 1
                                correct_sound.play()
                            else:
                                total_moves -= 1
                                wrong_sound.play()
                            break

                if reset_button_rect.collidepoint(mx, my) and resets_left > 0 and not show_game_over and not show_fun_fact:
                    reset_game_overlap()
                    print(f"Resets left after button click: {resets_left}")
                elif BACK_BUTTON_RECT.collidepoint(mx, my):
                    return
                elif info_icon_rect.collidepoint(mx, my) and not show_game_over:
                    show_fun_fact = not show_fun_fact
                elif show_fun_fact and close_button_rect.collidepoint(mx, my):
                    show_fun_fact = False
                elif show_game_over and ok_button_rect.collidepoint(mx, my):
                    show_game_over = False
                    game_state = "menu"
                    return
        if not show_game_over:
            if len(assembled_fragments) == len(level_fragments_overlap[current_level]):
                show_game_over = True
                game_over_message = "Success! Genome Assembled!"
                if not sound_played:
                    very_happy_sound.play()
                    sound_played = True
            elif total_moves <= 0 or (time_limit is not None and (time.time() - start_time >= time_limit)):
                show_game_over = True
                game_over_message = "Game Over! Out of moves or time."
                if not sound_played:
                    failure_sound.play()
                    sound_played = True
        draw_back_button(screen)
        draw_reset_button(resets_left, reset_button_rect, screen)
        aligned_data = get_aligned_fragments_pixelwise()
        for fragment, x, y in aligned_data:
             draw_kmer_text(fragment, x + font.size(fragment)[0] // 2, y + font.get_linesize() // 2, font)
        if not submitted:
            for i, rect in enumerate(fragment_rects):
                total_width = sum(font.size(base)[0] for base in fragments[i]) + (len(fragments[i]) - 1) * 5
                total_width += 20
                rect.width = total_width
                rect.height = 50
                pygame.draw.rect(screen, PINK, rect, border_radius=8)
                pygame.draw.rect(screen, BLACK, rect, 2, border_radius=8)
                x_offset = rect.x + 10
                y_offset = rect.y + 10
                for base in fragments[i]:
                    color = {"A": BLUE, "C": RED, "G": GREEN, "T": YELLOW}.get(base, WHITE)
                    for dx in range(-2, 3):
                        for dy in range(-2, 3):
                            if dx != 0 or dy != 0:
                                shadow = font.render(base, True, BLACK)
                                screen.blit(shadow, (x_offset + dx, y_offset + dy))
                    screen.blit(font.render(base, True, color), (x_offset, y_offset))
                    x_offset += font.size(base)[0] + 5

        score_text = FONT.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (20, 20))
        moves_text = FONT.render(f"Moves Left: {max(0, total_moves)}", True, BLACK)
        screen.blit(moves_text, (20, 50))
        resets_text = FONT.render(f"Resets Left: {resets_left}", True, BLACK)
        screen.blit(resets_text, (20, 80))

        if time_limit is not None:
            time_left = max(0, int(time_limit - (time.time() - start_time)))
            timer_text = FONT.render(f"Time Left: {time_left}s", True, BLACK)
            screen.blit(timer_text, (WIDTH - 200, 20))
        draw_reset_button(resets_left, reset_button_rect, screen)
        pygame.draw.circle(screen, LIGHT_PINK, info_icon_rect.center, 15)
        screen.blit(font.render("i", True, BLACK), (info_icon_rect.x + 8, info_icon_rect.y))
        if show_fun_fact:
            pygame.draw.rect(screen, LIGHT_PINK, fun_fact_rect, border_radius=12)
            pygame.draw.rect(screen, BLACK, fun_fact_rect, 2, border_radius=12)
            pygame.draw.rect(screen, RED, close_button_rect)
            pygame.draw.line(screen, WHITE, close_button_rect.topleft, close_button_rect.bottomright, 2)
            pygame.draw.line(screen, WHITE, close_button_rect.topright, close_button_rect.bottomleft, 2)
            for idx, line in enumerate(fun_fact_text):
                screen.blit(small_font.render(line, True, BLACK), (fun_fact_rect.x + 10, fun_fact_rect.y + 10 + idx * 18))
        if show_game_over:
            popup = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 100, 400, 180)
            pygame.draw.rect(screen, LIGHT_PINK, popup, border_radius=15)
            pygame.draw.rect(screen, BLACK, popup, 3, border_radius=15)
            lines = game_over_message.split("\n")  # Support multi-line messages
            for i, line in enumerate(lines):
               text = font.render(line, True, BLACK)
               screen.blit(text, (popup.centerx - text.get_width() // 2, popup.y + 40 + i * 30))
            pygame.draw.rect(screen, RED, ok_button_rect, border_radius=10)
            screen.blit(font.render("OK", True, WHITE), (ok_button_rect.x + 25, ok_button_rect.y + 7))
        pygame.display.flip()
        clock.tick(60)

running = True
clock = pygame.time.Clock()

while running:
    screen.fill(MEDIUM_PURPLE)
    buttons = draw_level_menu()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for name, rect, game, level in buttons:
                if rect.collidepoint(event.pos):
                    game_state = game
                    current_level = level
                    if game_state == "overlap":
                        if current_level == "Intermediate" or current_level == "Pro" or current_level == "Beginner":
                            resets_left = 5
                        if current_level == "Intermediate":
                            time_limit = 90
                        elif current_level == "Pro":
                            time_limit = 60
                        else:
                            time_limit = None

                        show_instruction_screen_overlap()
                        start_time = time.time() if time_limit is not None else None
                        game_loop_overlap(current_level)

                    elif game_state == "hamiltonian":
                        game_loop_hamiltonian(current_level)
                    elif game_state == "debruijn":
                        game_loop_debruijn(current_level)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
