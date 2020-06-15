from ursina import *


app = Ursina()

r = 8
for i in range(1, r):
    t = i/r
    s = 4*i
    print(s)
    grid = Entity(model=Grid(s,s), scale=s, color=color.color(0,0,.8,lerp(.8,0,t)), rotation_x=90, position=(-s/2, i/1000, -s/2))
    subgrid = duplicate(grid)
    subgrid.model = Grid(s*4, s*4)
    subgrid.color = color.color(0,0,.4,lerp(.8,0,t))
    EditorCamera()

app.run()

# # Text.default_font = 'VeraMono.ttf'
# gender_selection = ButtonGroup(('man', 'woman', 'other'))
# on_off_switch = ButtonGroup(('off', 'on'), min_selection=1, y=-.1, default='on', selected_color=color.red)
#
#
# def on_value_changed():
#     print('set gender:', gender_selection.value)
#
#
# gender_selection.on_value_changed = on_value_changed
#
#
# def on_value_changed():
#     print('turn:', on_off_switch.value)
#
#
# on_off_switch.on_value_changed = on_value_changed
#
# window.color = color._32


#
# Draggable
#
# if __name__ == '__main__':
#     app = Ursina()
#
#     Entity(model='plane', scale=8, texture='white_cube', texture_scale=(8, 8))
#     draggable_button = Draggable(scale=.1, text='drag me', position=(-.5, 0))
#     world_space_draggable = Draggable(parent=scene, model='cube', color=color.azure, plane_direction=(0, 1, 0))
#
#     EditorCamera(rotation=(30, 10, 0))
#     world_space_draggable.drop = Func(print, 'dropped cube')
#
#     app.run()

## Dropdown
# if __name__ == '__main__':
#     from ursina.prefabs.dropdown_menu import DropdownMenu, DropdownMenuButton
#
#     app = Ursina()
#     # DropdownMenu(text='File')
#     DropdownMenu('File', buttons=(
#         DropdownMenuButton('New'),
#         DropdownMenuButton('Open'),
#         DropdownMenu('Reopen Project', buttons=(
#             DropdownMenuButton('Project 1'),
#             DropdownMenuButton('Project 2'),
#             )),
#         DropdownMenuButton('Save'),
#         DropdownMenu('Options', buttons=(
#             DropdownMenuButton('Option a'),
#             DropdownMenuButton('Option b'),
#             )),
#         DropdownMenuButton('Exit'),
#         ))
#
#     app.run()

# Exit button
# '''
# This is the button in the upper right corner.
# You can click on it or press Shift+Q to close the program.
# To disable it, set window.exit_button.enabled to False
# '''
# app = Ursina()
# app.run()


# Health bar

# if __name__ == '__main__':
#     app = Ursina()
#
#     health_bar_1 = HealthBar(bar_color=color.lime.tint(-.25), roundness=.5, value=50)
#
#     def input(key):
#         if key == '+' or key == '+ hold':
#             health_bar_1.value += 10
#         if key == '-' or key == '- hold':
#             health_bar_1.value -= 10
#
#     app.run()
