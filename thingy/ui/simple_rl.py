from ursina import *
from ursina.prefabs.input_field import InputField

import fontawesome as fa

# print(fa.icons['thumbs-up'])


if __name__ == '__main__':
    app = Ursina()
    # WindowPanel(
    #     title='Custom Window',
    #     content=(
    #         Text('leflaijfae\njofeoijfw'),
    #         Button(text='test', color=color.green),
    #         Space(height=1),
    #         Text('leflaijfae\njofeoijfw'),
    #         InputField()
    #         # ButtonGroup(('test', 'eslk', 'skffk'))
    #     )
    # )
    glyphs = "ТЋУЎФХЦЧЏШЩЪЫЬ"
    font = '/home/cvasquez/envs/env_1/lib/python3.6/site-packages/fontawesome/static/fontawesome/webfonts/fa-brands-400.ttf'
    Text('''X🏠 by\n😃 ТЋУЎФХЦЧЏШЩЪЫЬ\nʕ •ᴥ•ʔゝ''', origin=(0,0), scale=6, color=color._20, y=.15, resolution=300, font=font)



    app.run()