import random

from utils.memory import gc_decorator, logged_gc
from utils.palette import BLACK, WHITE, colorwheel

logged_gc("Modules Imported")


def reverseString(s):
    res = []
    for i in range(len(s) - 1, -1, -1):
        res.append(s[i])
    return "".join(res)


class CellGrid:

    text_color = WHITE
    random_grid_density = 0.33
    reset_every = 1
    leave_after = 1

    def __init__(self, gameboard, run_forever=False):
        self.run_forever = run_forever
        self.board = gameboard
        self.reset(self.board.b1)
        self.board.set_clock_color(self.text_color)

    @gc_decorator
    def run(self):
        generations = 0
        old_text = ""
        first_run = True
        while True:

            new_text = self.board.get_time_string()
            if new_text != old_text:
                print(f"Updating time: {new_text}")
                print(f"Generations: {generations}")
                old_text = new_text
                self.board.set_clock_color(self.text_color)
                self.board.set_clock(new_text)

                if not first_run:
                    print("Checking for game exit conditions.")
                    last_digits = int(new_text[-2:])

                    # Leave this game to start another.
                    if not self.run_forever and last_digits % self.leave_after == 0:
                        print(f"Leaving Game after {generations} generations.")
                        return

                    # Reset the board.
                    if last_digits % self.reset_every == 0:
                        print("Restarting Game.")
                        self.reset(self.board.b1)
                        generations = 0

            if not self.board.process_inputs():
                print(f"Leaving Game after {generations} generations.")
                return

            self.board.display.root_group = self.board.g1
            self.apply_life_rule(self.board.b1, self.board.b2)
            generations += 1

            if not self.board.process_inputs():
                print(f"Leaving Game after {generations} generations.")
                return

            self.board.display.root_group = self.board.g2
            res = self.apply_life_rule(self.board.b2, self.board.b1)
            generations += 1

            if not res:
                print(f"Game has ended after {generations} generations.")
                self.reset(self.board.b1)
                generations = 0
            first_run = False

    @gc_decorator
    def reset(self, output):
        self.board.reset_palette()
        filler = random.choice(
            [
                self.randomize,
                self.rainbow_wave,
                self.rainbow_horizontal,
                self.rainbow_vertical,
            ]
        )
        filler(output)

    def randomize(self, output):
        for i in range(output.height * output.width):
            if random.random() < self.random_grid_density:
                output[i] = random.randint(1, self.board.max_colors - 1)
            else:
                output[i] = 0

    def rainbow_wave(self, output):
        for i in range(output.height * output.width):
            if random.random() < self.random_grid_density:
                output[i] = (i % (self.board.max_colors - 1)) + 1
            else:
                output[i] = 0

    def rainbow_vertical(self, output):
        width = output.width
        height = output.height

        # The offset means we can start the rainbow at any point in the spectrum.
        offset = random.randint(0, width)
        spectrum_size = width / (self.board.max_colors - 1)

        for y in range(height):
            yyy = y * width
            for x in range(width):
                if random.random() < self.random_grid_density:
                    adjusted_x = (x + offset) % width
                    output[x + yyy] = int(adjusted_x / spectrum_size) + 1
                else:
                    output[x + yyy] = 0

    def rainbow_horizontal(self, output):
        width = output.width
        height = output.height

        # The offset means we can start the rainbow at any point in the spectrum.
        offset = random.randint(0, height)
        spectrum_size = height / (self.board.max_colors - 1)

        for y in range(height):
            yyy = y * width
            for x in range(width):
                if random.random() < self.random_grid_density:
                    adjusted_y = (y + offset) % height
                    output[x + yyy] = int(adjusted_y / spectrum_size) + 1
                else:
                    output[x + yyy] = 0


class CellLine(CellGrid):

    current_color = None
    reset_on_full = True

    @gc_decorator
    def apply_life_rule(self, old, new):
        width = old.width
        height = old.height
        grid_size = width * height
        cell_count = 0
        has_cells = False
        for y in range(height):
            if y == 0:
                has_cells = self.first_row(old, new)
                continue

            yyy = y * width
            ym1 = ((y + height - 1) % height) * width
            for x in range(width):
                new[x + yyy] = old[x + ym1]
                if new[x + yyy] > 0:
                    cell_count += 1
                    has_cells = True

        if self.reset_on_full and cell_count == (grid_size - width):
            return False

        return has_cells

    @gc_decorator
    def reset(self, output):
        print("Rule reset.")
        self.board.reset_palette()
        self.one_color = random.random() < 0.2
        if self.one_color:
            self.board.palette[1] = colorwheel(random.randint(0, 255))
            start_color = 1
        else:
            self.current_color = random.randint(1, self.board.max_colors - 1)
            start_color = self.current_color

        self.board.clear_background()

        if self.starting_cells == 1:
            output[output.width // 2] = start_color
        else:
            for i in range(self.starting_cells):
                output[random.randint(0, output.width - 1)] = start_color

    def first_row(self, old, new):
        raise NotImplementedError()


class CellRules(CellLine):
    current_color = None
    reset_every = 5
    starting_cells = 1
    rule_number = 30

    def first_row(self, old, new):
        y = 0

        if self.one_color:
            color = 1
        else:
            if not self.current_color:
                self.current_color = random.randint(1, self.board.max_colors)
            else:
                self.current_color += 1
                if self.current_color >= self.board.max_colors:
                    self.current_color = 1
            color = self.current_color

        has_cells = False

        for x in range(old.width):
            left = "1" if old[((x - 1) % old.width)] > 0 else "0"
            current = "1" if old[x] > 0 else "0"
            right = "1" if old[((x + 1) % old.width)] > 0 else "0"
            triggered_rule = int(f"{left}{current}{right}", 2)
            if self.rule_flipped[triggered_rule] == "1":
                new[x + y] = color
                has_cells = True
            else:
                new[x + y] = 0

        return has_cells

    def reset(self, output):
        binary_rule = "{0:08b}".format(self.rule_number)
        self.rule_flipped = reverseString(binary_rule)
        super().reset(output)


class CellTotalistic(CellLine):

    code = 777
    num_colors = 3
    rule = []
    starting_cells = 1

    def convert_code_to_ruleset(self, code, num_colors):
        max_sum = (num_colors - 1) * 3
        ruleset = []
        while code > 0:
            ruleset.append(code % num_colors)
            code //= num_colors
        # Pad with zeros for sums that are not covered
        while len(ruleset) <= max_sum:
            ruleset.append(0)
        return ruleset

    def first_row(self, old, new):
        y = 0
        has_cells = False
        for x in range(old.width):
            left = old[((x - 1) % old.width)]
            current = old[x]
            right = old[((x + 1) % old.width)]
            total = left + current + right
            new[x + y] = self.rule[total]

            if new[x + y] > 0:
                has_cells = True

        return has_cells

    def reset(self, output):
        self.board.reset_palette(8)
        self.board.clear_background()
        self.rule = self.convert_code_to_ruleset(self.code, self.num_colors)
        if self.starting_cells == 1:
            output[output.width // 2] = 1
        else:
            for i in range(self.starting_cells):
                output[random.randint(0, output.width - 1)] = 1


class CellCreep(CellGrid):
    reset_every = 5
    creeps = []
    min_creeps = 1
    max_creeps = 15
    toggle_clock = False

    density_count = []

    @gc_decorator
    def apply_life_rule(self, old, new):
        width = old.width
        height = old.height
        grid_size = width * height
        lit_cells = 0
        for y in range(height):
            yyy = y * width
            for x in range(width):
                new[x + yyy] = old[x + yyy]
                if new[x + yyy] > 0:
                    lit_cells += 1

        for creep in self.creeps:
            self.process_creep(creep, old, new)

        DENSITY_KEEP = 5
        density = lit_cells / grid_size
        self.density_count.append(density)
        if len(self.density_count) > DENSITY_KEEP:
            self.density_count.pop(0)

        if self.toggle_clock:
            density_values = len(self.density_count)
            if density_values >= DENSITY_KEEP:
                rolling_density = sum(self.density_count) / len(self.density_count)
                print(f"Rolling Density: {rolling_density}")
                if density > 0.70:
                    self.board.set_clock_color(BLACK)

        return True

    def process_creep(self, creep, old, new):
        raise NotImplementedError()

    @gc_decorator
    def reset(self, output):
        self.board.clear_background()
        self.board.set_clock_color(WHITE)
        self.creeps = []
        self.place_creeps(output)

    def place_creeps(self, output):

        # Heavy bias towards 2 creeps, as it has the prettiest output.
        if random.random() < 0.4:
            creep_count = 2
        else:
            # Note that this also has a chance to be 2.
            creep_count = random.randint(self.min_creeps, self.max_creeps)

        if creep_count == 1:
            creep = self.new_creep(output)
            creep["x"] = output.width // 2
            creep["y"] = output.height // 2
            self.creeps.append(creep)
            return

        for i in range(random.randint(self.min_creeps, self.max_creeps)):
            self.creeps.append(self.new_creep(output))

    def new_creep(self, output):
        raise NotImplementedError()
