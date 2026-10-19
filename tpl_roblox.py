"""Roblox / Lua templates (plain Lua syntax that also runs in Roblox's Luau)."""
from tplkit import kit

CATEGORY = "Roblox / Lua"
TEMPLATES, add = kit(CATEGORY)
RUNNABLE = set()
PHRASES = []

SERVER = "Put this in a Script inside ServerScriptService."
CLIENT = "Put this in a LocalScript inside StarterPlayer > StarterPlayerScripts."
PART = "Put this in a Script inside the Part (Workspace)."


def lua(id, title, kw, code, how, phrases, precise=None):
    add(id, title, kw, lua=(code, precise, how))
    for p in phrases:
        PHRASES.append((p, id, "lua"))


SLOTS = {
    "NUMBER": [(r"\b(?:walk\s*speed|walkspeed|speed|jump\s*power|jumppower|jump\s*height|gravity|health|damage|coins?|cooldown|seconds?)\D{0,20}?(\d+(?:\.\d+)?)", lambda m: m.group(1))],
}

lua("roblox_walkspeed", "Set a player's WalkSpeed",
    {"walkspeed": 8, "speed": 3, "walk": 3, "roblox": 1, "faster": 2, "run": 1},
    '''-- Sets every player's WalkSpeed when their character spawns (default is 16)
local Players = game:GetService("Players")
local SPEED = __NUMBER|50__

local function onCharacter(character)
	local humanoid = character:WaitForChild("Humanoid")
	humanoid.WalkSpeed = SPEED
end

local function onPlayer(player)
	player.CharacterAdded:Connect(onCharacter)
	if player.Character then
		onCharacter(player.Character)
	end
end

Players.PlayerAdded:Connect(onPlayer)
for _, player in ipairs(Players:GetPlayers()) do
	onPlayer(player)
end
''', SERVER + " Change SPEED to taste. To affect only yourself in a LocalScript, use Players.LocalPlayer.",
    ["Create lua code for a script that sets my walkspeed to 50 in roblox", "roblox script to make players run faster walkspeed 30",
     "lua walkspeed script"],
    precise='''-- Sets every player's WalkSpeed (clamped to 0-200) when their character spawns
local Players = game:GetService("Players")
local SPEED = math.clamp(__NUMBER|50__, 0, 200)

local function onCharacter(character)
	local humanoid = character:WaitForChild("Humanoid", 10)
	if humanoid then
		humanoid.WalkSpeed = SPEED
	end
end

local function onPlayer(player)
	player.CharacterAdded:Connect(onCharacter)
	if player.Character then
		onCharacter(player.Character)
	end
end

Players.PlayerAdded:Connect(onPlayer)
for _, player in ipairs(Players:GetPlayers()) do
	onPlayer(player)
end
''')

lua("roblox_jumppower", "Set JumpPower / JumpHeight",
    {"jumppower": 8, "jump": 3, "power": 1, "higher": 2, "jumpheight": 8, "roblox": 1},
    '''local Players = game:GetService("Players")
local JUMP_POWER = __NUMBER|100__ -- default is 50

local function onCharacter(character)
	local humanoid = character:WaitForChild("Humanoid")
	humanoid.UseJumpPower = true
	humanoid.JumpPower = JUMP_POWER
end

local function onPlayer(player)
	player.CharacterAdded:Connect(onCharacter)
	if player.Character then
		onCharacter(player.Character)
	end
end

Players.PlayerAdded:Connect(onPlayer)
for _, player in ipairs(Players:GetPlayers()) do
	onPlayer(player)
end
''', SERVER, ["roblox script to set jump power to 100", "make players jump higher in roblox lua"])

lua("roblox_gravity", "Change the game's gravity",
    {"gravity": 8, "workspace": 1, "moon": 3, "floaty": 3, "roblox": 1},
    '''-- Default gravity is 196.2
workspace.Gravity = __NUMBER|50__
''', SERVER, ["roblox script to change gravity", "lua low gravity moon jump roblox"])

lua("roblox_god_mode", "God mode / max health",
    {"god": 6, "godmode": 8, "invincible": 6, "health": 3, "immortal": 5, "forcefield": 3, "roblox": 1},
    '''local Players = game:GetService("Players")

local function onCharacter(character)
	local humanoid = character:WaitForChild("Humanoid")
	humanoid.MaxHealth = math.huge
	humanoid.Health = math.huge
	humanoid.HealthChanged:Connect(function()
		if humanoid.Health < humanoid.MaxHealth then
			humanoid.Health = humanoid.MaxHealth
		end
	end)
end

Players.PlayerAdded:Connect(function(player)
	player.CharacterAdded:Connect(onCharacter)
end)
''', SERVER, ["roblox god mode script", "lua script make players invincible in roblox"])

lua("roblox_kill_brick", "Kill brick (lava part)",
    {"kill": 6, "brick": 5, "lava": 6, "deadly": 3, "touched": 2, "die": 3, "obby": 2, "roblox": 1},
    '''local part = script.Parent

part.Touched:Connect(function(hit)
	local humanoid = hit.Parent:FindFirstChildOfClass("Humanoid")
	if humanoid then
		humanoid.Health = 0
	end
end)
''', PART, ["roblox kill brick script", "lua lava part that kills the player when touched"])

lua("roblox_damage_brick", "Damage part (hurts over time)",
    {"damage": 6, "hurt": 5, "harm": 3, "spikes": 3, "touched": 1, "roblox": 1},
    '''local part = script.Parent
local DAMAGE = __NUMBER|10__
local COOLDOWN = 1
local lastHit = {}

part.Touched:Connect(function(hit)
	local humanoid = hit.Parent:FindFirstChildOfClass("Humanoid")
	if not humanoid then return end
	local now = os.clock()
	if lastHit[humanoid] and now - lastHit[humanoid] < COOLDOWN then return end
	lastHit[humanoid] = now
	humanoid:TakeDamage(DAMAGE)
end)
''', PART, ["roblox part that damages players 20 when touched", "lua spike damage script"])

lua("roblox_heal_pad", "Healing pad",
    {"heal": 6, "healing": 6, "regen": 4, "regenerate": 4, "medkit": 3, "pad": 2, "roblox": 1},
    '''local part = script.Parent
local HEAL = __NUMBER|25__
local COOLDOWN = 2
local busy = false

part.Touched:Connect(function(hit)
	local humanoid = hit.Parent:FindFirstChildOfClass("Humanoid")
	if humanoid and not busy then
		busy = true
		humanoid.Health = math.min(humanoid.Health + HEAL, humanoid.MaxHealth)
		task.wait(COOLDOWN)
		busy = false
	end
end)
''', PART, ["roblox healing pad script", "lua script that heals the player when they touch a part"])

lua("roblox_speed_pad", "Speed pad / boost pad",
    {"speed": 3, "pad": 4, "boost": 5, "booster": 5, "temporary": 2, "roblox": 1},
    '''local part = script.Parent
local BOOST_SPEED = __NUMBER|60__
local DURATION = 5

part.Touched:Connect(function(hit)
	local humanoid = hit.Parent:FindFirstChildOfClass("Humanoid")
	if humanoid and humanoid.WalkSpeed ~= BOOST_SPEED then
		local old = humanoid.WalkSpeed
		humanoid.WalkSpeed = BOOST_SPEED
		task.wait(DURATION)
		humanoid.WalkSpeed = old
	end
end)
''', PART, ["roblox speed pad boost script", "lua speed boost pad that lasts 5 seconds"])

lua("roblox_jump_pad", "Jump pad / launch pad",
    {"jump": 3, "pad": 4, "launch": 6, "launcher": 5, "bounce": 4, "trampoline": 4, "roblox": 1},
    '''local part = script.Parent
local FORCE = __NUMBER|100__

part.Touched:Connect(function(hit)
	local root = hit.Parent:FindFirstChild("HumanoidRootPart")
	if root then
		root.AssemblyLinearVelocity = Vector3.new(root.AssemblyLinearVelocity.X, FORCE, root.AssemblyLinearVelocity.Z)
	end
end)
''', PART, ["roblox jump pad script", "lua launch pad that bounces the player up"])

lua("roblox_checkpoints", "Checkpoint spawns (obby)",
    {"checkpoint": 8, "checkpoints": 8, "spawn": 3, "respawn": 3, "obby": 4, "stage": 2, "roblox": 1},
    '''-- Name your checkpoint parts "Checkpoint1", "Checkpoint2", ... inside a Folder called "Checkpoints" in Workspace
local Players = game:GetService("Players")
local folder = workspace:WaitForChild("Checkpoints")
local reached = {}

for _, part in ipairs(folder:GetChildren()) do
	part.Touched:Connect(function(hit)
		local player = Players:GetPlayerFromCharacter(hit.Parent)
		if player then
			reached[player] = part
		end
	end)
end

Players.PlayerAdded:Connect(function(player)
	player.CharacterAdded:Connect(function(character)
		local checkpoint = reached[player]
		if checkpoint then
			task.wait()
			character:PivotTo(checkpoint.CFrame + Vector3.new(0, 4, 0))
		end
	end)
end)

Players.PlayerRemoving:Connect(function(player)
	reached[player] = nil
end)
''', SERVER, ["roblox obby checkpoint system script", "lua checkpoints that respawn the player at the last checkpoint"])

lua("roblox_teleport_part", "Teleport part (touch to teleport)",
    {"teleport": 7, "teleporter": 7, "portal": 5, "warp": 5, "destination": 2, "roblox": 1},
    '''-- Put a Part named "Destination" in Workspace
local part = script.Parent
local destination = workspace:WaitForChild("Destination")

part.Touched:Connect(function(hit)
	local character = hit.Parent
	if character:FindFirstChildOfClass("Humanoid") then
		character:PivotTo(destination.CFrame + Vector3.new(0, 4, 0))
	end
end)
''', PART, ["roblox teleport part script", "lua portal that teleports the player to another part"])

lua("roblox_leaderstats", "Leaderstats (coins / points on the leaderboard)",
    {"leaderstats": 9, "leaderboard": 6, "coins": 3, "points": 3, "score": 3, "cash": 3, "stats": 2, "roblox": 1},
    '''local Players = game:GetService("Players")

Players.PlayerAdded:Connect(function(player)
	local leaderstats = Instance.new("Folder")
	leaderstats.Name = "leaderstats"
	leaderstats.Parent = player

	local coins = Instance.new("IntValue")
	coins.Name = "Coins"
	coins.Value = 0
	coins.Parent = leaderstats
end)
''', SERVER, ["roblox leaderstats script with coins", "lua create a leaderboard with points and cash"])

lua("roblox_coin_pickup", "Coin pickup",
    {"coin": 6, "coins": 4, "pickup": 6, "collect": 5, "collectible": 5, "gem": 3, "roblox": 1},
    '''-- Needs the leaderstats script (a "Coins" value in player.leaderstats). Put this Script inside the coin Part.
local Players = game:GetService("Players")
local coin = script.Parent
local VALUE = __NUMBER|1__
local used = false

coin.Touched:Connect(function(hit)
	if used then return end
	local player = Players:GetPlayerFromCharacter(hit.Parent)
	local stats = player and player:FindFirstChild("leaderstats")
	if stats and stats:FindFirstChild("Coins") then
		used = true
		stats.Coins.Value = stats.Coins.Value + VALUE
		coin:Destroy()
	end
end)
''', "Put this in a Script inside the coin Part. Needs the leaderstats script.", ["roblox coin pickup script", "lua collectible coin that gives the player a point"])

lua("roblox_datastore", "Save and load player data (DataStore)",
    {"datastore": 9, "save": 5, "saving": 5, "load": 3, "persist": 4, "data": 2, "store": 2, "roblox": 1},
    '''local Players = game:GetService("Players")
local DataStoreService = game:GetService("DataStoreService")
local store = DataStoreService:GetDataStore("PlayerData")

local function load(player)
	local stats = Instance.new("Folder")
	stats.Name = "leaderstats"
	stats.Parent = player
	local coins = Instance.new("IntValue")
	coins.Name = "Coins"
	coins.Parent = stats

	local ok, saved = pcall(function()
		return store:GetAsync("Player_" .. player.UserId)
	end)
	coins.Value = (ok and saved) or 0
end

local function save(player)
	local stats = player:FindFirstChild("leaderstats")
	if not stats then return end
	local ok, err = pcall(function()
		store:SetAsync("Player_" .. player.UserId, stats.Coins.Value)
	end)
	if not ok then
		warn("Could not save " .. player.Name .. ": " .. tostring(err))
	end
end

Players.PlayerAdded:Connect(load)
Players.PlayerRemoving:Connect(save)
game:BindToClose(function()
	for _, player in ipairs(Players:GetPlayers()) do
		save(player)
	end
end)
''', SERVER + " Turn on Game Settings > Security > Enable Studio Access to API Services to test in Studio.",
    ["roblox datastore save player coins", "lua script to save and load player data in roblox"])

lua("roblox_proximity_prompt", "Proximity prompt (press E)",
    {"proximityprompt": 9, "proximity": 6, "prompt": 4, "interact": 4, "press": 2, "roblox": 1},
    '''local part = script.Parent
local prompt = Instance.new("ProximityPrompt")
prompt.ActionText = "__REPLY|Open__"
prompt.ObjectText = "__NAME|Door__"
prompt.HoldDuration = 0
prompt.MaxActivationDistance = 10
prompt.Parent = part

prompt.Triggered:Connect(function(player)
	print(player.Name .. " used the prompt")
end)
''', PART, ["roblox proximity prompt script press e to interact", "lua proximityprompt that prints when triggered"])

lua("roblox_click_detector", "Click detector",
    {"clickdetector": 9, "click": 5, "clicked": 4, "mouse": 2, "roblox": 1},
    '''local part = script.Parent
local detector = Instance.new("ClickDetector")
detector.MaxActivationDistance = 20
detector.Parent = part

detector.MouseClick:Connect(function(player)
	print(player.Name .. " clicked the part")
	part.BrickColor = BrickColor.Random()
end)
''', PART, ["roblox click detector script that changes color", "lua click a part to do something"])

lua("roblox_door", "Door that opens and closes (tween)",
    {"door": 8, "doors": 6, "open": 3, "close": 2, "slide": 2, "gate": 4, "roblox": 1},
    '''local TweenService = game:GetService("TweenService")
local door = script.Parent
local closedCFrame = door.CFrame
local openCFrame = door.CFrame * CFrame.new(0, door.Size.Y, 0)
local info = TweenInfo.new(0.6, Enum.EasingStyle.Quad)
local isOpen = false

local prompt = Instance.new("ProximityPrompt")
prompt.ActionText = "Open"
prompt.Parent = door

prompt.Triggered:Connect(function()
	isOpen = not isOpen
	prompt.ActionText = isOpen and "Close" or "Open"
	TweenService:Create(door, info, {CFrame = isOpen and openCFrame or closedCFrame}):Play()
end)
''', PART, ["roblox door script that opens and closes", "lua sliding gate that opens"])

lua("roblox_tween_part", "Tween (animate) a part",
    {"tween": 9, "tweenservice": 9, "animate": 3, "move": 2, "smooth": 3, "roblox": 1},
    '''local TweenService = game:GetService("TweenService")
local part = script.Parent

local info = TweenInfo.new(__NUMBER|2__, Enum.EasingStyle.Sine, Enum.EasingDirection.InOut, -1, true)
local goal = {Position = part.Position + Vector3.new(0, 10, 0)}
TweenService:Create(part, info, goal):Play()
''', PART, ["roblox tween a part up and down", "lua tweenservice move part script"])

lua("roblox_spinning_part", "Spinning part",
    {"spin": 8, "spinning": 8, "rotate": 6, "rotating": 6, "turn": 2, "roblox": 1},
    '''local part = script.Parent
local SPEED = math.rad(__NUMBER|90__) -- degrees per second
local RunService = game:GetService("RunService")

RunService.Heartbeat:Connect(function(dt)
	part.CFrame = part.CFrame * CFrame.Angles(0, SPEED * dt, 0)
end)
''', PART + " Set Anchored = true on the part.", ["roblox spinning part script", "lua rotate a part forever"])

lua("roblox_day_night", "Day / night cycle",
    {"day": 4, "night": 4, "cycle": 5, "daynight": 8, "clock": 2, "time": 2, "lighting": 2, "roblox": 1},
    '''local Lighting = game:GetService("Lighting")
local MINUTES_PER_SECOND = 1 -- game minutes that pass each real second

while true do
	Lighting:SetMinutesAfterMidnight(Lighting:GetMinutesAfterMidnight() + MINUTES_PER_SECOND)
	task.wait(1)
end
''', SERVER, ["roblox day night cycle script", "lua script to make time pass in lighting"])

lua("roblox_gui_button", "GUI with a button",
    {"gui": 6, "button": 6, "screengui": 8, "textbutton": 7, "menu": 2, "ui": 3, "roblox": 1},
    '''-- LocalScript in StarterPlayerScripts: builds a button and reacts to clicks
local Players = game:GetService("Players")
local playerGui = Players.LocalPlayer:WaitForChild("PlayerGui")

local gui = Instance.new("ScreenGui")
gui.Name = "MyGui"
gui.ResetOnSpawn = false
gui.Parent = playerGui

local button = Instance.new("TextButton")
button.Size = UDim2.new(0, 200, 0, 50)
button.Position = UDim2.new(0.5, -100, 0.8, 0)
button.Text = "__REPLY|Click me__"
button.Parent = gui

button.MouseButton1Click:Connect(function()
	print("Button clicked")
end)
''', CLIENT, ["roblox gui button script", "lua create a screengui with a textbutton"])

lua("roblox_timer_gui", "Countdown timer on screen",
    {"gui": 3, "label": 4, "textlabel": 7, "onscreen": 4, "screen": 2, "timer": 1, "countdown": 1, "roblox": 1},
    '''-- LocalScript in StarterPlayerScripts
local Players = game:GetService("Players")
local playerGui = Players.LocalPlayer:WaitForChild("PlayerGui")

local gui = Instance.new("ScreenGui")
gui.Parent = playerGui
local label = Instance.new("TextLabel")
label.Size = UDim2.new(0, 200, 0, 50)
label.Position = UDim2.new(0.5, -100, 0, 10)
label.TextScaled = true
label.Parent = gui

for seconds = __NUMBER|60__, 0, -1 do
	label.Text = string.format("%02d:%02d", seconds // 60, seconds % 60)
	task.wait(1)
end
label.Text = "Time's up!"
''', CLIENT, ["roblox timer gui textlabel 60 seconds", "lua timer text label on screen"])

lua("roblox_sprint", "Sprint (hold shift to run)",
    {"sprint": 9, "shift": 5, "running": 3, "hold": 1, "stamina": 2, "roblox": 1},
    '''local Players = game:GetService("Players")
local UserInputService = game:GetService("UserInputService")

local WALK, RUN = 16, __NUMBER|32__
local player = Players.LocalPlayer

local function setSpeed(speed)
	local character = player.Character
	local humanoid = character and character:FindFirstChildOfClass("Humanoid")
	if humanoid then
		humanoid.WalkSpeed = speed
	end
end

UserInputService.InputBegan:Connect(function(input, processed)
	if not processed and input.KeyCode == Enum.KeyCode.LeftShift then
		setSpeed(RUN)
	end
end)

UserInputService.InputEnded:Connect(function(input)
	if input.KeyCode == Enum.KeyCode.LeftShift then
		setSpeed(WALK)
	end
end)
''', CLIENT, ["roblox sprint script hold shift to run", "lua shift to sprint"])

lua("roblox_double_jump", "Double jump",
    {"double": 5, "twice": 5, "doublejump": 9, "extra": 2, "airjump": 6, "roblox": 1},
    '''local Players = game:GetService("Players")
local UserInputService = game:GetService("UserInputService")

local player = Players.LocalPlayer
local jumps = 0
local MAX_JUMPS = 2

local function setup(character)
	local humanoid = character:WaitForChild("Humanoid")
	jumps = 0
	humanoid.StateChanged:Connect(function(_, new)
		if new == Enum.HumanoidStateType.Landed then
			jumps = 0
		end
	end)
	UserInputService.JumpRequest:Connect(function()
		if humanoid:GetState() == Enum.HumanoidStateType.Freefall and jumps < MAX_JUMPS - 1 then
			jumps = jumps + 1
			humanoid:ChangeState(Enum.HumanoidStateType.Jumping)
		end
	end)
end

player.CharacterAdded:Connect(setup)
if player.Character then
	setup(player.Character)
end
''', CLIENT, ["roblox double jump script", "lua allow players to jump twice"])

lua("roblox_chat_commands", "Admin chat commands (/kick, /speed)",
    {"admin": 7, "command": 3, "commands": 3, "chat": 5, "kick": 5, "ban": 3, "moderator": 3, "roblox": 1},
    '''local Players = game:GetService("Players")
local ADMINS = {[1] = true} -- replace 1 with your UserId

local function runCommand(player, message)
	local args = string.split(message, " ")
	local cmd = string.lower(args[1])
	if cmd == "/kick" and args[2] then
		local target = Players:FindFirstChild(args[2])
		if target then
			target:Kick("Kicked by an admin")
		end
	elseif cmd == "/speed" and tonumber(args[2]) then
		local humanoid = player.Character and player.Character:FindFirstChildOfClass("Humanoid")
		if humanoid then
			humanoid.WalkSpeed = math.clamp(tonumber(args[2]), 0, 200)
		end
	end
end

Players.PlayerAdded:Connect(function(player)
	player.Chatted:Connect(function(message)
		if ADMINS[player.UserId] and string.sub(message, 1, 1) == "/" then
			runCommand(player, message)
		end
	end)
end)
''', SERVER, ["roblox admin commands script", "lua chat command to kick players"])

lua("roblox_tool_sword", "Sword / tool that damages on hit",
    {"sword": 9, "tool": 5, "weapon": 5, "melee": 4, "slash": 3, "damage": 1, "roblox": 1},
    '''-- Script inside a Tool that has a Part named "Handle"
local tool = script.Parent
local handle = tool:WaitForChild("Handle")
local DAMAGE = __NUMBER|20__
local canHit = true

tool.Activated:Connect(function()
	canHit = true
	task.delay(0.5, function() canHit = false end)
end)

handle.Touched:Connect(function(hit)
	local humanoid = hit.Parent:FindFirstChildOfClass("Humanoid")
	if canHit and humanoid and hit.Parent ~= tool.Parent then
		canHit = false
		humanoid:TakeDamage(DAMAGE)
	end
end)
''', "Put this in a Script inside a Tool (Tool > Handle part).", ["roblox sword script that damages", "lua melee weapon tool"])

lua("roblox_raycast_gun", "Gun using raycasting",
    {"gun": 8, "raycast": 9, "shoot": 6, "shooting": 6, "fire": 3, "bullet": 4, "blaster": 4, "roblox": 1},
    '''-- Tool with a LocalScript and a RemoteEvent named "Fire" inside the tool.
-- Server Script (inside the Tool):
local tool = script.Parent
local fire = tool:WaitForChild("Fire")
local DAMAGE = __NUMBER|25__
local RANGE = 300

fire.OnServerEvent:Connect(function(player, targetPosition)
	local character = player.Character
	local root = character and character:FindFirstChild("HumanoidRootPart")
	if not root or typeof(targetPosition) ~= "Vector3" then return end

	local params = RaycastParams.new()
	params.FilterDescendantsInstances = {character}
	params.FilterType = Enum.RaycastFilterType.Exclude

	local direction = (targetPosition - root.Position).Unit * RANGE
	local result = workspace:Raycast(root.Position, direction, params)
	local humanoid = result and result.Instance.Parent:FindFirstChildOfClass("Humanoid")
	if humanoid then
		humanoid:TakeDamage(DAMAGE)
	end
end)

-- LocalScript (inside the Tool):
-- script.Parent.Activated:Connect(function()
--     script.Parent.Fire:FireServer(game.Players.LocalPlayer:GetMouse().Hit.Position)
-- end)
''', "Server Script inside a Tool; add a RemoteEvent called Fire and the small LocalScript from the comment.",
    ["roblox gun script with raycast", "lua shooting tool raycast damage"])

lua("roblox_remote_event", "RemoteEvent (client talks to server)",
    {"remoteevent": 9, "remote": 6, "event": 2, "fireserver": 8, "onserverevent": 8, "client": 2, "server": 2, "roblox": 1},
    '''-- 1) Create a RemoteEvent named "MyEvent" in ReplicatedStorage.
-- 2) Server Script (ServerScriptService):
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local event = ReplicatedStorage:WaitForChild("MyEvent")

event.OnServerEvent:Connect(function(player, message)
	if typeof(message) ~= "string" then return end -- never trust the client
	print(player.Name .. " says: " .. message)
	event:FireClient(player, "Got it!")
end)

-- 3) LocalScript (StarterPlayerScripts):
-- local event = game:GetService("ReplicatedStorage"):WaitForChild("MyEvent")
-- event:FireServer("hello")
-- event.OnClientEvent:Connect(function(reply) print(reply) end)
''', SERVER, ["roblox remote event script client to server", "lua fireserver onserverevent example"])

lua("roblox_round_system", "Round system (intermission and rounds)",
    {"round": 7, "rounds": 7, "intermission": 8, "minigame": 4, "match": 3, "lobby": 4, "roblox": 1},
    '''local Players = game:GetService("Players")
local INTERMISSION, ROUND_TIME, MIN_PLAYERS = 15, __NUMBER|60__, 2

local status = Instance.new("StringValue")
status.Name = "Status"
status.Parent = game:GetService("ReplicatedStorage")

while true do
	repeat
		status.Value = "Waiting for players..."
		task.wait(1)
	until #Players:GetPlayers() >= MIN_PLAYERS

	for t = INTERMISSION, 1, -1 do
		status.Value = "Next round in " .. t
		task.wait(1)
	end

	for t = ROUND_TIME, 1, -1 do
		status.Value = "Round ends in " .. t
		task.wait(1)
	end
	status.Value = "Round over!"
	task.wait(3)
end
''', SERVER + " Show Status.Value in a TextLabel from a LocalScript.", ["roblox round system with intermission", "lua game rounds script"])

lua("roblox_teams", "Team assignment",
    {"team": 7, "teams": 7, "teamcolor": 6, "assign": 3, "balance": 3, "roblox": 1},
    '''local Players = game:GetService("Players")
local Teams = game:GetService("Teams")

local function makeTeam(name, color)
	local team = Instance.new("Team")
	team.Name = name
	team.TeamColor = color
	team.AutoAssignable = false
	team.Parent = Teams
	return team
end

local teams = {makeTeam("Red", BrickColor.new("Bright red")), makeTeam("Blue", BrickColor.new("Bright blue"))}

Players.PlayerAdded:Connect(function(player)
	local smallest = teams[1]
	for _, team in ipairs(teams) do
		if #team:GetPlayers() < #smallest:GetPlayers() then
			smallest = team
		end
	end
	player.Team = smallest
end)
''', SERVER, ["roblox team assign script red and blue", "lua balance players into teams"])

lua("roblox_npc_follow", "NPC that follows the nearest player (pathfinding)",
    {"npc": 8, "follow": 6, "chase": 6, "pathfinding": 9, "zombie": 5, "enemy": 3, "roblox": 1},
    '''-- Script inside an NPC Model that has a Humanoid and HumanoidRootPart
local Players = game:GetService("Players")
local PathfindingService = game:GetService("PathfindingService")
local npc = script.Parent
local humanoid = npc:WaitForChild("Humanoid")
local root = npc:WaitForChild("HumanoidRootPart")

local function nearestPlayerRoot()
	local best, bestDistance = nil, math.huge
	for _, player in ipairs(Players:GetPlayers()) do
		local target = player.Character and player.Character:FindFirstChild("HumanoidRootPart")
		if target then
			local d = (target.Position - root.Position).Magnitude
			if d < bestDistance then best, bestDistance = target, d end
		end
	end
	return best
end

while true do
	local target = nearestPlayerRoot()
	if target then
		local path = PathfindingService:CreatePath()
		path:ComputeAsync(root.Position, target.Position)
		if path.Status == Enum.PathStatus.Success then
			local waypoints = path:GetWaypoints()
			if waypoints[2] then
				humanoid:MoveTo(waypoints[2].Position)
			end
		end
	end
	task.wait(0.3)
end
''', "Put this in a Script inside the NPC Model.", ["roblox npc follows the player with pathfinding", "lua zombie that chases players"])

lua("roblox_music", "Play music / sound",
    {"music": 8, "sound": 6, "song": 5, "audio": 4, "soundtrack": 5, "play": 1, "roblox": 1},
    '''local sound = Instance.new("Sound")
sound.SoundId = "rbxassetid://__NUMBER|1837879082__" -- replace with an audio asset id you have access to
sound.Looped = true
sound.Volume = 0.5
sound.Parent = workspace
sound:Play()
''', SERVER, ["roblox background music script", "lua play a looping sound"])

lua("roblox_fly", "Fly (for your own game)",
    {"fly": 9, "flying": 9, "flight": 6, "hover": 3, "roblox": 1},
    '''local Players = game:GetService("Players")
local UserInputService = game:GetService("UserInputService")
local RunService = game:GetService("RunService")

local player = Players.LocalPlayer
local SPEED = __NUMBER|50__
local flying = false

UserInputService.InputBegan:Connect(function(input, processed)
	if not processed and input.KeyCode == Enum.KeyCode.F then
		flying = not flying
		local humanoid = player.Character and player.Character:FindFirstChildOfClass("Humanoid")
		if humanoid then
			humanoid.PlatformStand = flying
		end
	end
end)

RunService.RenderStepped:Connect(function()
	if not flying then return end
	local character = player.Character
	local root = character and character:FindFirstChild("HumanoidRootPart")
	if not root then return end
	local camera = workspace.CurrentCamera
	local direction = Vector3.zero
	if UserInputService:IsKeyDown(Enum.KeyCode.W) then direction = direction + camera.CFrame.LookVector end
	if UserInputService:IsKeyDown(Enum.KeyCode.S) then direction = direction - camera.CFrame.LookVector end
	if UserInputService:IsKeyDown(Enum.KeyCode.A) then direction = direction - camera.CFrame.RightVector end
	if UserInputService:IsKeyDown(Enum.KeyCode.D) then direction = direction + camera.CFrame.RightVector end
	root.AssemblyLinearVelocity = direction * SPEED
end)
''', CLIENT + " Press F to toggle flying. Use it in your own games (e.g. admin/testing tools).", ["roblox fly script press f", "lua flying script for my game"])

lua("roblox_kick_player", "Kick or ban a player by name / UserId",
    {"kick": 6, "ban": 6, "banlist": 6, "banned": 5, "blacklist": 4, "roblox": 1},
    '''local Players = game:GetService("Players")
local BANNED = {[1] = true} -- UserIds that cannot join

Players.PlayerAdded:Connect(function(player)
	if BANNED[player.UserId] then
		player:Kick("You are banned from this game.")
	end
end)
''', SERVER, ["roblox ban list script", "lua kick banned players when they join"])

lua("roblox_badge", "Award a badge",
    {"badge": 9, "badges": 9, "award": 4, "achievement": 4, "roblox": 1},
    '''local BadgeService = game:GetService("BadgeService")
local Players = game:GetService("Players")
local BADGE_ID = __NUMBER|0__ -- your badge id from the Creator Dashboard

Players.PlayerAdded:Connect(function(player)
	local ok, has = pcall(BadgeService.UserHasBadgeAsync, BadgeService, player.UserId, BADGE_ID)
	if ok and not has then
		pcall(BadgeService.AwardBadge, BadgeService, player.UserId, BADGE_ID)
	end
end)
''', SERVER, ["roblox award badge script", "lua give players a badge when they join"])

lua("roblox_gamepass", "Game pass / developer product purchase prompt",
    {"gamepass": 9, "pass": 3, "marketplace": 5, "purchase": 5, "robux": 5, "product": 3, "shop": 2, "roblox": 1},
    '''local MarketplaceService = game:GetService("MarketplaceService")
local Players = game:GetService("Players")
local GAME_PASS_ID = __NUMBER|0__ -- your game pass id

-- Prompt a purchase (call from a server script, e.g. when a part is touched)
local function offer(player)
	MarketplaceService:PromptGamePassPurchase(player, GAME_PASS_ID)
end

-- Check ownership
local function owns(player)
	local ok, result = pcall(MarketplaceService.UserOwnsGamePassAsync, MarketplaceService, player.UserId, GAME_PASS_ID)
	return ok and result
end

Players.PlayerAdded:Connect(function(player)
	if owns(player) then
		print(player.Name .. " owns the pass")
	end
end)
''', SERVER, ["roblox game pass script", "lua robux purchase prompt"])

lua("roblox_cooldown", "Cooldown / debounce pattern",
    {"cooldown": 8, "debounce": 8, "delay": 2, "limit": 2, "spam": 3, "roblox": 1},
    '''local COOLDOWN = __NUMBER|3__ -- seconds
local lastUsed = {}

local function tryUse(player)
	local now = os.clock()
	if lastUsed[player] and now - lastUsed[player] < COOLDOWN then
		return false
	end
	lastUsed[player] = now
	return true
end

game:GetService("Players").PlayerRemoving:Connect(function(player)
	lastUsed[player] = nil
end)

-- Usage: if tryUse(player) then ... end
''', SERVER, ["roblox cooldown script", "lua cooldown for abilities"])

lua("roblox_part_spawner", "Spawn parts at random positions",
    {"spawner": 8, "spawn": 3, "random": 3, "falling": 3, "parts": 2, "clone": 3, "roblox": 1},
    '''local INTERVAL = __NUMBER|1__
local AREA = 100

while true do
	local part = Instance.new("Part")
	part.Size = Vector3.new(4, 4, 4)
	part.BrickColor = BrickColor.Random()
	part.Position = Vector3.new(math.random(-AREA, AREA), 80, math.random(-AREA, AREA))
	part.Parent = workspace
	game:GetService("Debris"):AddItem(part, 10)
	task.wait(INTERVAL)
end
''', SERVER, ["roblox script that spawns random falling parts", "lua part spawner"])

lua("roblox_welcome_message", "Welcome message when a player joins",
    {"welcome": 8, "join": 5, "joins": 5, "joined": 5, "announce": 3, "message": 2, "roblox": 1},
    '''local Players = game:GetService("Players")
local StarterGui = game:GetService("StarterGui")

Players.PlayerAdded:Connect(function(player)
	print("Welcome, " .. player.Name .. "! (" .. #Players:GetPlayers() .. " players online)")
end)
''', SERVER, ["roblox welcome message on join", "lua print when a player joins"])

lua("roblox_respawn_time", "Custom respawn time",
    {"respawn": 6, "respawntime": 9, "death": 3, "died": 3, "roblox": 1},
    '''local Players = game:GetService("Players")
Players.RespawnTime = __NUMBER|2__
''', SERVER, ["roblox respawn time script", "lua change how fast players respawn"])

lua("roblox_camera", "Change the camera (first person / fixed view)",
    {"camera": 9, "firstperson": 7, "person": 2, "view": 3, "fov": 5, "zoom": 3, "roblox": 1},
    '''local Players = game:GetService("Players")
local player = Players.LocalPlayer

player.CameraMode = Enum.CameraMode.LockFirstPerson -- or Classic
workspace.CurrentCamera.FieldOfView = __NUMBER|90__
''', CLIENT, ["roblox first person camera script", "lua change field of view"])

lua("roblox_color_change", "Change a part's color / material",
    {"color": 5, "colour": 5, "brickcolor": 8, "material": 4, "neon": 4, "rainbow": 5, "roblox": 1},
    '''local part = script.Parent

-- Rainbow color cycle
local hue = 0
while true do
	hue = (hue + 0.01) % 1
	part.Color = Color3.fromHSV(hue, 1, 1)
	task.wait(0.03)
end
''', PART, ["roblox rainbow part script", "lua change part color over time"])
