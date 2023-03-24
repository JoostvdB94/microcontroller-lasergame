ir_remote_codes=[
    "30",
    "18",
    "7a",
]

def get_team(code):
    try:
        return ir_remote_codes.index(code) + 1
    except:
        return -1;

def get_code(team):
    if team < len(ir_remote_codes):
        return ir_remote_codes[team - 1]
    else:
        return -1