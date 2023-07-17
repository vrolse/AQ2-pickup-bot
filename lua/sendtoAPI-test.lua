local APIaddr = "http://test.server.api:1234/" -- change this
local team1 = nil
local team2 = nil

function runWithTimeout(command, timeout)
    local timeoutCommand = string.format("timeout %d %s", timeout, command)
    return os.execute(timeoutCommand)
end

function LogMessage(msg)
    local matchend = string.match(msg, "Match is over.+")
    if matchend ~= nil then
        team1 = gi.cvar("t1", '').string
        team2 = gi.cvar("t2", '').string
        map = gi.cvar("mapname", '').string
        hostname = gi.cvar("hostname", "").string
        local name = string.gsub(hostname, "%s+", "")
        local fname = string.gsub(name, "[^%w_]", "")

        -- Get player data
        local playerData = {}
        for i, plr in pairs(ex.players) do
            if plr.name ~= "[MVDSPEC]" then
                local frags = ex.ClientStats(i, STAT_FRAGS)
                table.insert(playerData, { name = plr.name, score = frags })
            end
        end

        -- Function to convert a Lua value to its JSON representation
        local function jsonEncode(value)
            if type(value) == "string" then
                return '"' .. value:gsub('[%c"\\]', {
                    ['\t'] = '\\t',
                    ['\n'] = '\\n',
                    ['\r'] = '\\r',
                    ['"'] = '\\"',
                    ['\\'] = '\\\\',
                }) .. '"'
            elseif type(value) == "table" then
                local parts = {}
                for k, v in pairs(value) do
                    table.insert(parts, jsonEncode(k) .. ":" .. jsonEncode(v))
                end
                return "{" .. table.concat(parts, ",") .. "}"
            else
                return tostring(value)
            end
        end

        -- Convert the 'playerData' table to a JSON string
        local playerJsonStrings = {}
        for _, player in ipairs(playerData) do
            table.insert(playerJsonStrings, jsonEncode(player))
        end

        -- Join player JSON strings into an array
        local playerJsonArray = "[" .. table.concat(playerJsonStrings, ",") .. "]"

        local jsonPayload = string.format('{"ID":"%s","name":"%s","T1":"%s","T2":"%s","map":"%s","players":%s}', fname, hostname, team1, team2, map, playerJsonArray)
        local cmd = string.format("curl -X PUT -H 'Content-Type: application/json' -d '%s' %s", jsonPayload, APIaddr)

        local exitCode = runWithTimeout(cmd, 1)  -- Timeout set to 1 second so server does not freeze for too long

        if exitCode == 124 then
            print('Timed out')
        elseif exitCode == 0 then
            print('Match score sent!')
        else
            print('Error code:', exitCode)
        end

        return true
    end
end
