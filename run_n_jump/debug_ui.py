from .math_helper import vec2
from .text import text2d


def create_debug_ui(system_names):
    result = []
    total_time = text2d("Total time={total_time:.3f}ms", position=vec2(0, 0), font_size=9)
    result.append(total_time)

    # for index, system_name in enumerate(system_names):
    #     system_time = text2d(system_name + "={" + system_name + ":.3f}ms", position=vec2(100, 90 + index * 10),
    #                          font_size=11)
    #     result.append(system_time)

    return result
