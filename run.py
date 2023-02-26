import flask
from flask import Response
import requests
import re
import json
import os
from utils import GithubInteractions
import scoreforger.ScoreForger as ScoreForger

verhash = ScoreForger.md5(f"{ScoreForger.get_osu_runtime_dir()}/osu.Game.dll")
print(f"ver_check:: Version hash -> {verhash}")

app = flask.Flask(__name__, template_folder='templates', static_folder='static')

print(f"mod_check:: Getting all the mods from osu's github repo...")

osu_mods_dict = []

osu_repo_tree = GithubInteractions.TreeToList(GithubInteractions.GetRepoDirectory('ppy', 'osu'))
osu_mods = [x for x in osu_repo_tree if re.match(r'osu.Game.Rulesets.\w+/Mods/\w+.cs', x)]
osu_always_mods = [x for x in osu_repo_tree if re.match(r'osu.Game/Rulesets/Mods/\w+.cs', x)]
osu_mods += osu_always_mods

del osu_repo_tree
del osu_always_mods

print(f"mod_check:: Getting all the valid mods from the cache...")
if not os.path.exists('mods_cache._'):
    with open('mods_cache._', 'w') as f:
        f.write('{}')

if not os.path.exists('mods_ignore._'):
    with open('mods_ignore._', 'w') as f:
        f.write('[]')

with open('mods_cache._', 'r') as f:
    osu_mods_dict = json.loads(f.read())

with open('mods_ignore._', 'r') as f:
    ignore_list = json.loads(f.read())

print(f"mod_check:: Found {len(osu_mods)} mods. Checking the validity...")
for mod in osu_mods:
    if mod in osu_mods_dict:
        continue
    if mod in ignore_list:
        continue

    mod_file = GithubInteractions.GetRepoFile('ppy', 'osu', mod)
    if re.search(r'public override string Acronym => @?"(\w+)";', mod_file):
        mod_acronym = re.search(r'public override string Acronym => @?"(\w+)";', mod_file).group(1)

        print(f"mod_check:: cache < {mod} ({mod_acronym})")
        osu_mods_dict[mod] = mod_acronym

    else:
        print(f"mod_check:: ignore < {mod}")
        ignore_list.append(mod)

mods_cache = open('mods_cache._', 'w')
mods_cache.write(json.dumps(osu_mods_dict))
mods_cache.close()

mods_ignore = open('mods_ignore._', 'w')
mods_ignore.write(json.dumps(ignore_list))
mods_ignore.close()


print(f"mod_check:: Done! {len(osu_mods_dict)} mods are valid. {len(ignore_list)} mods are invalid. {len(osu_mods) - len(osu_mods_dict) - len(ignore_list)} mods are not checked. (This is normal.)")

del osu_mods

@app.route('/')
def index():
    return flask.render_template('index.html')

@app.route('/api/get-possible-mods')
def get_possible_mods():
    return Response(json.dumps(osu_mods_dict), mimetype='application/json')

@app.route('/api/get-beatmap-info')
def get_beatmap_info():
    beatmap_id = flask.request.args.get('beatmap_id')
    beatmap_info = requests.get(f'https://osu.ppy.sh/api/get_beatmaps?k={os.environ["osu_api_key"]}&s={beatmap_id}').json()
    return Response(json.dumps(beatmap_info), mimetype='application/json')

@app.route('/api/try-login')
def try_login():
    username = flask.request.args.get('username')
    password = flask.request.args.get('password')
    data = {
        'grant_type': (None, 'password', 'text/plain', {'charset': 'utf-8'}),
        'client_id': (None, '5', 'text/plain', {'charset': 'utf-8'}),
        'client_secret': (None, 'FGc9GAtyHzeQDshWP5Ah7dega8hJACAJpQtw6OXk', 'text/plain', {'charset': 'utf-8'}),
        'scope': (None, '*', 'text/plain', {'charset': 'utf-8'}),
        'username': (None, username, 'text/plain', {'charset': 'utf-8'}),
        'password': (None, password, 'text/plain', {'charset': 'utf-8'})
    }
    login_info = requests.post(f'https://osu.ppy.sh/oauth/token', files=data)
    if (login_info.status_code != 200):
        return Response(json.dumps({'error': 'invalid_credentials'}), mimetype='application/json')
    login_json = login_info.json()
    return Response(json.dumps(login_json), mimetype='application/json')

@app.route('/api/forge-score', methods=['POST'])
def forge_score():
    # print all json data
    req = flask.request.get_json()

    username = req['username']
    password = req['password']
    score_data = req['score_data']
    beatmap_id = req['beatmap_id']

    CreateScoreData = {
        "ruleset": score_data['ruleset_id'],
        "passstate": bool(score_data['passstate']),
        "total_score": score_data['total_score'],
        "accuracy": score_data['accuracy'],
        "max_combo": score_data['max_combo'],
        "rank": score_data['rank'],
        "mods": score_data['mods'],
        "statistics": score_data['statistics']
    }

    forger = ScoreForger.ScoreForger(username, password, verhash)
    score = forger.create_score(score_data['beatmap_id'], score_data['ruleset_id'])
    scoredata = ScoreForger.CreateScoreData(**CreateScoreData)
    res = forger.submit_score(score, scoredata)
    return Response(json.dumps(res), mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True)
