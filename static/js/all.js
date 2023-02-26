const POSSIBLE_MODS = {};
var ENABLED_MODS = [];
var Token = null;
var Credentials = null;

window.onload = async () =>
{
    let mods = await fetch('/api/get-possible-mods');
    mods = await mods.json();
    // for key, value
    for (var [key, value] of Object.entries(mods))
    {
        key = key.match(/Mods\/(\w+).cs/)[1];
        POSSIBLE_MODS[key] = value;
    }

    let possibleModsEl = document.querySelector(".possible-mods");
    for (var [key, value] of Object.entries(POSSIBLE_MODS))
    {
        let wrapper = document.createElement("div");
        wrapper.style.display = "inline-block";
        wrapper.style.margin = "2px 2px";
        let input = document.createElement("input");
        input.type = "checkbox";
        input.className = "btn-check";
        input.id = "btn-check-" + key;
        input.autocomplete = "off";
        
        let label = document.createElement("label");
        label.className = "btn btn-outline-success";
        label.htmlFor = "btn-check-" + key;
        label.dataset.mod = value;
        label.dataset.tippyContent = key;
        label.title = key;
        label.innerText = value;

        label.onclick = () =>
        {
            let mod = label.dataset.mod;
            if (label.classList.contains("active"))
            {
                label.classList.remove("active");
                ENABLED_MODS = ENABLED_MODS.filter(x => x != mod);
            }
            else
            {
                label.classList.add("active");
                ENABLED_MODS.push(mod);
            }
            console.log(ENABLED_MODS);
        }

        wrapper.appendChild(input);
        wrapper.appendChild(label);
        possibleModsEl.appendChild(wrapper);
        
    }


    document.getElementById("score-data-maplink").onchange = async () =>
    {
        console.log(document.getElementById("score-data-maplink").value);
        let mapId = document.getElementById("score-data-maplink").value.match(/beatmapsets\/(\d+)/)[1];
        document.getElementById("beatmap-image").src = `https://assets.ppy.sh/beatmaps/${mapId}/covers/cover@2x.jpg?${Date.now()}`;
        // get beatmap info
        try
        {
            let beatmap = await fetch(`/api/get-beatmap-info?beatmap_id=${mapId}`);
            beatmap = await beatmap.json();
            let _zName = beatmap[0].artist + " - " + beatmap[0].title;
            document.getElementById("beatmap-name").innerText = _zName;
        }
        catch (e)
        {
            console.log(e);
            document.getElementById("beatmap-name").innerText = "Failed to get beatmap info";
        }
    }

    document.getElementById("user-auth-test").onclick = async (e) =>
    {
        e.preventDefault();
        let username = document.getElementById("score-auth-username").value;
        let password = document.getElementById("score-auth-password").value;
        let user = await fetch(`/api/try-login?username=${username}&password=${password}`);
        user = await user.json();
        if('error' in user)
        {
            alert("Failed to login. Check your username and password.");
            return;
        }
        Token = user.access_token;
        Credentials = {
            username: username,
            password: password
        };
        e.target.className = "btn btn-success disabled";
        e.target.innerText = "Logged in";
        e.target.disabled = true;
        document.getElementById("score-auth-username").disabled = true;
        document.getElementById("score-auth-password").disabled = true;
    }
}


function GetScoreData()
{
    return {
        "beatmap_id": document.getElementById("score-data-maplink").value.match(/beatmapsets\/\d+#\w+\/(\d+)/)[1],
        "ruleset_id": document.getElementById("score-data-ruleset").value,
        "mods": ENABLED_MODS,
        "total_score": document.getElementById("score-data-score").value,
        "max_combo": document.getElementById("score-data-combo").value,
        "accuracy": document.getElementById("score-data-accuracy").value,
        "rank": document.getElementById("score-data-rank").value,
        "passstate": document.getElementById("score-data-passstate").checked,
        "statistics": {
            "miss": document.getElementById("score-data-miss").value,
            "ok": document.getElementById("score-data-ok").value,
            "great": document.getElementById("score-data-great").value,
            "small_tick_miss": 0,
            "small_tick_hit": 0,
            "large_tick_hit": 0,
            "small_bonus": 0,
            "large_bonus": 0,
            "ignore_miss": 0,
            "ignore_hit": 0
        }
    }
}

async function SubmitScore(score_data)
{
    if (Credentials == null || Token == null)
    {
        alert("You need to login first.");
        return;
    }
    let res = await fetch(`/api/forge-score`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            "beatmap_id": score_data.beatmap_id,
            "username": Credentials.username,
            "password": Credentials.password,
            "score_data": score_data
        })
    });
    res = await res.json();
    if('error' in res)
    {
        alert("Failed to submit score. Check your username and password.\n"+res.error);
        return;
    }
    alert("Score submitted successfully!");
    
}