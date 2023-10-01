-- vrol's attempt on lua-scripting..
--[[

v1.0 Send map result to AQ2-pickup bot "API"

]]--

local APIaddr = "http://test.server.api:1234/" -- change this
local team1 = nil
local team2 = nil

function runWithTimeout(command, timeout)
    local timeoutCommand = string.format("timeout %d %s", timeout, command)
    local handle = io.popen(timeoutCommand, "r")
    local output = handle:read("*a")
    handle:close()

    return output
end

function escapeString(str)
    return str:gsub('[%z\1-\31\128-\255"\'\\]', {
        ['\a'] = '\\a',
        ['\b'] = '\\b',
        ['\f'] = '\\f',
        ['\n'] = '\\n',
        ['\r'] = '\\r',
        ['\t'] = '\\t',
        ['\v'] = '\\v',
        ['"'] = '\\"',
        ['\\'] = '\\\\',
        ['|'] = '\\|',
    })
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
            local frags = ex.ClientStats(i, STAT_FRAGS)
            table.insert(playerData, { name = escapeString(plr.name), score = frags })
        end

        -- Convert the 'playerData' table to a JSON string
        local playerJsonStrings = {}
        for _, player in ipairs(playerData) do
            local jsonStr = string.format('{"name":"%s","score":%d}', player.name, player.score)
            table.insert(playerJsonStrings, jsonStr)
        end

        -- Join player JSON strings into an array
        local playerJsonArray = "[" .. table.concat(playerJsonStrings, ",") .. "]"

        local jsonPayload = string.format('{"ID":"%s","name":"%s","T1":"%s","T2":"%s","map":"%s","players":%s}', fname, hostname, team1, team2, map, playerJsonArray)
        local cmd = string.format("curl -X PUT -H \"Content-Type: application/json\" -d %q %s", jsonPayload, APIaddr)

        local output = runWithTimeout(cmd, 1)

        if output == nil then
            print('Error executing the command')
        else
            print('Match score sent!')
        end

        return true
    end
end
