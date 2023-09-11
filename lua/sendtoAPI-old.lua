-- vrol's attempt on lua-scriptning.. 
-- Test to send map result to AQ2-pickup bot API

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
        local jsonPayload = string.format('{"ID":"%s","name":"%s","T1":"%s","T2":"%s","map":"%s"}', fname, hostname, team1, team2, map)
        local cmd = string.format("curl -X PUT -H 'Content-Type: application/json' -d '%s' %s", jsonPayload, APIaddr)

        local exitCode = runWithTimeout(cmd, 1)  -- Timeout set to 1 seconds so server do not freeze for too long

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