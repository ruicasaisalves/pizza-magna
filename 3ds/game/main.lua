--[[ Pizza Magna for the Nintendo 3DS (LÖVE Potion), prototype: the Kitchen and the Menu.
     Kitchen. Bottom screen (touch): the bench, as in the browser game (320 wide, title strip on top, pizza,
     bowls, LCD). Top screen: the topping picker, dough and sauce, and the analysis (quality, cost, appeal, notes).
     Menu. Top screen: the house menu, one row a pizza. Bottom screen: the chosen pizza, its price
     (- / +), quality, cost and margin, and the buttons to edit, rename or remove it.
     Day: the LCD and the news on top, the street below (customers walk to our door or the rival's), then the
     close-of-day report. Contest: the next theme on top, the pizzas to enter below. Shop: ovens, pizzaiolos,
     flyers, supplier, market study. SELECT goes to the next screen (and L/R, outside the Kitchen).
     On a PC (LÖVE 11/12) the window shows the top screen above the bottom one, and the mouse is the stylus. ]]
local P = require("pizza")
local G = require("day")
local MUS = require("musica")
local RL = require("roomlib")   -- the room's rules (the room editor)   -- the browser game's tunes, recorded (tools/export_3ds_music.js)
local D, A, t = P.D, P.A, P.t

local CONSOLE = love._console ~= nil or love.system.getOS() == "Horizon" or love.system.getOS() == "3DS"
local BOTTOM_X, BOTTOM_Y = 40, 240   -- where the bottom screen sits in the PC window

-- text only the 3DS port has (the browser game has no buttons to explain)
local L3 = {
  en = { keys1 = "✚ choose   A whole/chopped   X turn   B undo   Y clear",
         kweek = "Topping of the week!", klow = "Least wanted this week", kcombo = "Combo", kcost = "Cost", ksugg = "Suggested price", kappeal = "Appeal",
         mkeys1 = "✚ pizza and price   A edit   X rename   Y remove", renamel = "Rename",
         quit = "Save and quit", startopt = "START options", rent = "Rent", sale = "Sale", on = "On", off = "Off", back = "Back", okeys = "✚ choose   A change   B back",
         dkeys = "A open the doors", drun = "✚ speed   B pause   A skip to closing", rkeys = "A continue",
         ckeys = "✚ pizza   A enter it", skeys = "✚ choose   A buy or choose   touch: hire, bank", stcols = { "Name", "Speed · skill", "Wage" },
         hkeys = "Y sales history", hback = "Y back to the day",
         citykeys = "✚ move   A rent, buy, go   Y close, sell   X zoom",
         edkeys = "L/R tab   ✚ choose   A take or buy   B back", edplace = "Drag it into the room (B: cancel)",
         edpick = "Drag to move   X sell (+{x})   B done", edhint = "Touch a piece in the room, drag it to move it", ednofit = "It doesn't fit there.",
         edroom = "Decorate the room",
         },
  pt = { keys1 = "✚ escolher   A inteiro/picado   X rodar   B desfazer   Y limpar",
         kweek = "Ingrediente da semana!", klow = "Pouco procurado esta semana", kcombo = "Combo", kcost = "Custo", ksugg = "Preço sugerido", kappeal = "Apelo",
         mkeys1 = "✚ pizza e preço   A editar   X nome   Y remover", renamel = "Mudar nome",
         quit = "Gravar e sair", startopt = "START opções", rent = "Arrenda", sale = "Venda", on = "Ligada", off = "Desligada", back = "Voltar", okeys = "✚ escolher   A mudar   B voltar",
         dkeys = "A abrir portas", drun = "✚ velocidade   B pausa   A saltar para o fecho", rkeys = "A continuar",
         ckeys = "✚ pizza   A inscrever", skeys = "✚ escolher   A comprar ou escolher   toque: contratar, banco", stcols = { "Nome", "Rapid. · arte", "Salário" },
         hkeys = "Y histórico de vendas", hback = "Y voltar ao dia",
         citykeys = "✚ mover   A arrendar, comprar, ir   Y fechar, vender   X zoom",
         edkeys = "L/R separador   ✚ escolher   A pegar ou comprar   B voltar", edplace = "Arrasta-o para a sala (B: cancelar)",
         edpick = "Arrasta para mudar   X vender (+{x})   B pronto", edhint = "Toca numa peça da sala e arrasta-a para a mudar", ednofit = "Não cabe aí.",
         edroom = "Decorar a sala",
         },
}
local function l3(k) return L3[P.lang()][k] end
local MINE_LOT = 1   -- the first shop's lot on the city map
for i, l in ipairs(D.CITY.LOTS) do if l.kind == "mine" then MINE_LOT = i end end

-- ---------------------------------------------------------------- state and save
--[[ S.name/S.editing: the pizza on the bench (no name yet = "New pizza"; editing = id of the menu pizza it came from).
     S.menu: the house menu, {id, name, dough, sauce, pieces, price}, as in the browser game. ]]
local S = { dough = "napo", sauce = "tomate", pieces = {}, sel = "fiambre", cut = "w", rot = {}, found = {}, lang = nil,
  name = nil, editing = nil, menu = nil, tab = "kitchen", msel = 1, nextId = 1, csel = 1, ssel = 1 }
local anim, report = nil, nil   -- the day running in the street; the close-of-day report on screen
local ED = nil                   -- the room editor, when open (Shop › Decorate the room)
local openEditor
local histOn = false             -- the Day's top screen shows the sales history instead of the LCD (Y)
local cleared = nil          -- the pizza the bin just cleared: undo on an empty bench brings it back
local dirty, saveTimer, saveFailed = false, 0, false   -- saveFailed: the last write failed (retried every 10 s)
local toasts = {}
local function toast(s)   -- a new message cuts the one on screen short, so a "press again" never waits in a queue
  if toasts[1] and toasts[1].time > .6 then toasts[1].time = .6 end
  toasts[#toasts + 1] = { s = s, time = 3 }
end
local an                     -- analysis of the pizza on the bench (recomputed on every change)

-- save.txt: one "key=value" a line; each menu pizza is a "pizza=" line of tab-separated fields
-- the shops on one "shops=" line, as a Lua table literal (the parked ones carry their data; pieces packed)
local function ser(v)
  local ty = type(v)
  if ty == "number" then return string.format("%.4g", v) == tostring(v) and tostring(v) or string.format("%.6f", v) end
  if ty == "boolean" then return tostring(v) end
  if ty == "string" then return '"' .. v:gsub("\\", "\\\\"):gsub('"', '\\"'):gsub("\n", "\\n"):gsub("\r", "") .. '"' end
  if ty ~= "table" then return "nil" end
  local out = {}
  for k, x in pairs(v) do
    if k ~= "an" then out[#out + 1] = (type(k) == "number" and ("[" .. k .. "]") or ("[" .. ser(k) .. "]")) .. "=" .. ser(x) end
  end
  return "{" .. table.concat(out, ",") .. "}"
end
local function shopsLine()
  local list = {}
  for i, sh in ipairs(S.shops) do
    local x = { hood = sh.hood, lot = sh.lot, traffic = sh.traffic, owned = sh.owned }
    if sh.data then
      local d = {}
      for k, v in pairs(sh.data) do d[k] = v end
      d.menu = {}
      for _, p in ipairs(sh.data.menu) do d.menu[#d.menu + 1] = { id = p.id, name = p.name, dough = p.dough, sauce = p.sauce, price = p.price, pk = P.packPieces(p.pieces) } end
      x.data = d
    end
    list[i] = x
  end
  return "shops=" .. ser(list)
end
local function readShops(val)
  local f = (loadstring or load)("return " .. val)
  local ok, list = pcall(f or error)
  if not ok or type(list) ~= "table" then return nil end
  for _, sh in ipairs(list) do
    if sh.data then
      for _, p in ipairs(sh.data.menu or {}) do
        local pieces = {}
        pcall(function() pieces = P.unpackPieces(p.pk or "") end)
        p.pieces, p.pk = pieces, nil
      end
      sh.data.hist, sh.data.lastSales, sh.data.staff = sh.data.hist or {}, sh.data.lastSales or {}, sh.data.staff or {}
    end
  end
  return list
end
local function save()
  local rot = {}
  for k, v in pairs(S.rot) do rot[#rot + 1] = k .. ":" .. v end
  local lines = {
    "lang=" .. P.lang(), "dough=" .. S.dough, "sauce=" .. S.sauce, "sel=" .. S.sel, "cut=" .. S.cut,
    "rot=" .. table.concat(rot, ","), "found=" .. table.concat(S.found, ","), "pieces=" .. P.packPieces(S.pieces),
    "name=" .. (S.name or ""), "editing=" .. (S.editing or ""), "tab=" .. S.tab, "msel=" .. S.msel, "nextid=" .. S.nextId, "menu=1",
    "day=" .. S.day, "money=" .. string.format("%.2f", S.money), "rep=" .. string.format("%.4f", S.rep), "ovens=" .. S.ovens,
    "loan=" .. string.format("%.2f", S.loan or 0), "candday=" .. (S.candDay or ""), "ads=" .. (S.ads and 1 or 0), "supplier=" .. S.supplier, "entry=" .. (S.contestEntry or ""),
    "music=" .. (MUS.on and 1 or 0), "musvol=" .. MUS.vol,
    "studyweek=" .. S.studyWeek, "over=" .. (S.over and 1 or 0), "goal=" .. (S.goalDone and 1 or 0),
    "rival=" .. table.concat({ S.rival.name, S.rival.q, string.format("%.2f", S.rival.price), S.rival.promo and 1 or 0 }, "\t"),
  }
  local sales = {}
  for id, n in pairs(S.lastSales) do sales[#sales + 1] = id .. ":" .. n end
  lines[#lines + 1] = "sales=" .. table.concat(sales, ",")
  lines[#lines + 1] = "cur=" .. S.cur
  lines[#lines + 1] = "room=" .. ser(G.room(S))
  lines[#lines + 1] = shopsLine()
  for _, n in ipairs(S.news) do
    local f = { n.k }
    for k, v in pairs(n.v) do f[#f + 1] = k .. "=" .. tostring(v):gsub("[\t\n]", " ") end
    lines[#lines + 1] = "news=" .. table.concat(f, "\t")
  end
  -- people: id, name, role, speed, second skill, wage, look (staff = the team, cand = today's candidates)
  for _, l in ipairs({ { "staff", S.staff }, { "cand", S.cands or {} } }) do
    for _, x in ipairs(l[2]) do lines[#lines + 1] = l[1] .. "=" .. table.concat({ x.id, x.n, x.r, x.sp, x.sk, x.w, x.v }, "\t") end
  end
  for _, h in ipairs(S.hist) do
    lines[#lines + 1] = "hist=" .. table.concat({ h.d, h.n, h.N, h.rv, string.format("%.2f", h.p), string.format("%.2f", h.v), string.format("%.2f", h.r), (h.top or ""):gsub("[\t\n]", " "), h.topN or 0, h.f and h.f[1] or "", h.f and h.f[2] or "", h.f and h.f[3] or "" }, "\t")
  end
  for _, c in ipairs(S.contestLog) do lines[#lines + 1] = "ctlog=" .. table.concat({ c.day, c.theme, c.pizza, c.pos, c.prize }, "\t") end
  for _, x in ipairs(S.tips) do lines[#lines + 1] = "tip=" .. table.concat({ x.day, x.seg, x.ing, x.combo or "" }, "\t") end
  for _, p in ipairs(S.menu) do
    lines[#lines + 1] = "pizza=" .. table.concat({ p.id, string.format("%.2f", p.price), p.dough, p.sauce, p.name, P.packPieces(p.pieces) }, "\t")
  end
  local ok = love.filesystem.write("save.txt", table.concat(lines, "\n") .. "\n")
  if not ok and not saveFailed then
    toast(P.lang() == "pt" and "Falha ao gravar no cartão SD." or "Could not save to the SD card.")
  end
  saveFailed = not ok
  dirty = not ok
  return ok
end
local function load()
  local ok, txt = pcall(love.filesystem.read, "save.txt")
  if not ok or not txt then return end
  local v, menu, news, ctlog, tips, people, hist = {}, {}, {}, {}, {}, { staff = {}, cand = {} }, {}
  local function fields(val) local f = {}; for x in (val .. "\t"):gmatch("([^\t]*)\t") do f[#f + 1] = x end; return f end
  for line in txt:gmatch("[^\n]+") do
    local k, val = line:match("^(%w+)=(.*)$")
    if k == "news" then
      local f = fields(val)
      local n = G.news(f[1])
      for q = 2, #f do local a, b = f[q]:match("^(%w+)=(.*)$"); if a then n.v[a] = b end end
      news[#news + 1] = n
    elseif k == "ctlog" then
      local f = fields(val)
      ctlog[#ctlog + 1] = { day = tonumber(f[1]) or 0, theme = f[2], pizza = f[3], pos = tonumber(f[4]) or 0, prize = tonumber(f[5]) or 0 }
    elseif k == "staff" or k == "cand" then
      local f = fields(val)
      if f[3] == "cook" or f[3] == "waiter" then
        local n = function(i, d) return math.max(1, math.min(5, tonumber(f[i]) or d)) end
        people[k][#people[k] + 1] = { id = f[1], n = f[2], r = f[3], sp = n(4, 3), sk = n(5, 3), w = tonumber(f[6]) or 30, v = tonumber(f[7]) or 0 }
      end
    elseif k == "hist" then
      local f = fields(val)
      local n = function(i) return tonumber(f[i]) or 0 end
      hist[#hist + 1] = { d = n(1), n = n(2), N = n(3), rv = n(4), p = n(5), v = n(6), r = n(7), top = f[8] or "", topN = n(9),
        f = (f[10] or "") ~= "" and { n(10), n(11), n(12) } or nil }   -- how they left (days before the faces have none)
    elseif k == "tip" then
      local f = fields(val)
      if D.SEG[f[2]] and D.ING[f[3]] then tips[#tips + 1] = { day = tonumber(f[1]) or 1, seg = f[2], ing = f[3], combo = f[4] ~= "" and f[4] or nil } end
    elseif k == "pizza" then
      local f = {}
      for x in (val .. "\t"):gmatch("([^\t]*)\t") do f[#f + 1] = x end
      if #f >= 6 and D.DOUGHS[f[3]] and D.SAUCES[f[4]] then
        local pieces = {}
        pcall(function() pieces = P.unpackPieces(f[6]) end)
        menu[#menu + 1] = { id = f[1], price = tonumber(f[2]) or 9, dough = f[3], sauce = f[4], name = f[5], pieces = pieces }
      end
    elseif k == "shops" then v.shops = readShops(val)
    elseif k then v[k] = val end
  end
  if v.menu then S.menu = menu end   -- saves from before the Menu get the starter pizzas
  if v.name and v.name ~= "" then S.name = v.name end
  if v.editing and v.editing ~= "" then S.editing = v.editing end
  if v.tab then S.tab = v.tab end
  MUS.init(v.music ~= "0", v.musvol)   -- music on unless turned off
  S.msel = tonumber(v.msel) or 1
  S.nextId = tonumber(v.nextid) or 1
  if v.day then   -- saves from before the restaurant start a new game in load (S.day stays nil)
    S.day, S.money, S.rep = tonumber(v.day) or 1, tonumber(v.money) or 1000, tonumber(v.rep) or 1
    S.ovens, S.ads, S.loan = tonumber(v.ovens) or 1, v.ads == "1", tonumber(v.loan) or 0
    -- the team; saves from before the staff profiles had a count of pizzaiolos (waiters were free): average people
    if #people.staff > 0 then S.staff = people.staff
    else local n = tonumber(v.cooks) or 1; S.staff = G.startStaff(S, n, math.ceil(n * 2 / 3)) end
    S.cands, S.candDay, S.hist = people.cand, tonumber(v.candday), hist
    -- the shops (saves from before the City: one shop on the first lot)
    S.shops = type(v.shops) == "table" and #v.shops > 0 and v.shops or { { lot = MINE_LOT } }
    if v.room then local f = (loadstring or load)("return " .. v.room); local ok, room = pcall(f or error); S.room = ok and room or nil end
    S.room = RL.ensure(S.room)   -- saves from before the room editor: the starter room
    S.cur = math.max(1, math.min(#S.shops, tonumber(v.cur) or 1))
    S.shops[S.cur].data = nil
    S.supplier = D.SUPPLIER[tonumber(v.supplier)] and tonumber(v.supplier) or 1
    S.contestEntry = v.entry ~= "" and v.entry or nil
    S.studyWeek, S.over, S.goalDone = tonumber(v.studyweek) or -1, v.over == "1", v.goal == "1"
    local f = fields(v.rival or "")
    S.rival = { name = f[1] ~= "" and f[1] or "Pizza Rápida", q = tonumber(f[2]) or 52, price = tonumber(f[3]) or 7, promo = f[4] == "1" }
    S.lastSales = {}
    for id, n in (v.sales or ""):gmatch("([%w_]+):(%d+)") do S.lastSales[id] = tonumber(n) end
    S.news, S.contestLog, S.tips = news, ctlog, tips
  end
  if not ({ kitchen = 1, menu = 1, day = 1, contest = 1, shop = 1, city = 1 })[S.tab] then S.tab = "kitchen" end
  if v.lang then S.lang = v.lang end
  if v.dough and D.DOUGHS[v.dough] then S.dough = v.dough end
  if v.sauce and D.SAUCES[v.sauce] then S.sauce = v.sauce end
  if v.sel and D.ING[v.sel] then S.sel = v.sel end
  if v.cut == "g" then S.cut = "g" end
  for k, n in (v.rot or ""):gmatch("([%w_]+):(%d)") do if D.ING[k] then S.rot[k] = tonumber(n) end end
  for id in (v.found or ""):gmatch("[%w_]+") do S.found[#S.found + 1] = id end
  if v.pieces and v.pieces ~= "" then pcall(function() S.pieces = P.unpackPieces(v.pieces) end) end
end

local function r2(v) return math.floor(v * 100 + .5) / 100 end

-- the three pizzas a new game starts with (freshState() in index.html; spread() lays a topping out in a spiral)
local function spread(id, n, rad, seed)
  local out = {}
  local function fx(v, d) local m = 10 ^ d; return (v < 0 and -1 or 1) * math.floor(math.abs(v) * m + .5) / m end
  for k = 0, n - 1 do
    local a, r = (k + seed) * 2.39996, rad * math.sqrt((k + .5) / n)
    out[#out + 1] = { i = id, x = fx(math.cos(a) * r, 3), y = fx(math.sin(a) * r, 3), r = fx((k * 1.7 + seed) % 6.28, 2) }
  end
  return out
end
local function join(...) local out = {}; for _, l in ipairs({ ... }) do for _, x in ipairs(l) do out[#out + 1] = x end end; return out end
local function starterMenu()
  local cheese = function() return spread("mozzarella", 11, .74, 0) end
  S.menu = {
    { id = "p1", name = "Margherita da Casa", dough = "napo", sauce = "tomate", price = 9, pieces = join(cheese(), spread("manjericao", 6, .62, 3)) },
    { id = "p2", name = t("start.fc"), dough = "napo", sauce = "tomate", price = 9, pieces = join(cheese(), spread("fiambre", 7, .66, 1), spread("cogumelos", 7, .6, 4)) },
    { id = "p3", name = t("start.pep"), dough = "napo", sauce = "tomate", price = 9, pieces = join(cheese(), spread("pepperoni", 9, .66, 2), spread("oregaos", 5, .55, 5)) },
  }
  S.nextId = 4
end
-- the restaurant at the start of a game (freshState() in index.html)
local function freshGame()
  S.day, S.money, S.rep, S.ovens, S.ads, S.supplier, S.loan = 1, 1000, 1, 1, false, 1, 0
  S.staff, S.cands, S.candDay, S.hist = {}, {}, nil, {}
  S.staff = G.startStaff(S, 1, 1)   -- one pizzaiolo and one waiter
  S.shops, S.cur = { { lot = MINE_LOT } }, 1
  S.rival = { name = "Pizza Rápida", q = 52, price = 7, promo = false }
  S.news = { G.news("nw.start") }
  S.contestEntry, S.contestLog, S.lastSales, S.tips, S.studyWeek = nil, {}, {}, {}, -1
  S.over, S.goalDone = false, false
end
local function newId()
  while true do
    local id = "p" .. S.nextId; S.nextId = S.nextId + 1
    local used = false
    for _, p in ipairs(S.menu) do if p.id == id then used = true end end
    if not used then return id end
  end
end
-- each menu pizza keeps its analysis until it changes (p.an = nil)
local function anOf(p) if not p.an then p.an = P.analyze(p) end; return p.an end
-- who picks each menu pizza (G.menuShares), worked out again only when a pizza, its price or its analysis changes
local sharesKey, sharesW
local function shares()
  local k = {}
  for _, p in ipairs(S.menu) do k[#k + 1] = p.id .. ":" .. p.price .. ":" .. tostring(anOf(p)) end
  k = table.concat(k, ",")
  if k ~= sharesKey then sharesKey, sharesW = k, G.menuShares(S, anOf) end
  return sharesW
end
local function copyPieces(ps) local out = {}; for k, x in ipairs(ps) do local c = {}; for kk, vv in pairs(x) do c[kk] = vv end; out[k] = c end; return out end

-- ---------------------------------------------------------------- toppings by group (the pantry tabs)
local catList = {}
local function buildCats()
  for _, c in ipairs(D.CATS) do catList[c] = {} end
  for _, id in ipairs(D.ING_ORDER) do local c = P.ingCat(id); catList[c][#catList[c] + 1] = id end
  local function favIdx(id) for k, f in ipairs(D.FAV) do if f == id then return k end end; return nil end
  for _, c in ipairs(D.CATS) do
    table.sort(catList[c], function(a, b)   -- the classics first, then A to Z in the player's language
      local fa, fb = favIdx(a), favIdx(b)
      if fa or fb then return (fa or 99) < (fb or 99) end
      return P.fold(P.ingName(a)) < P.fold(P.ingName(b))
    end)
  end
end
local function catOf(id) return P.ingCat(id) end
local function idxIn(list, v) for k, x in ipairs(list) do if x == v then return k end end; return 1 end

-- ---------------------------------------------------------------- the pizza being made
local function curCut() return (S.cut == "g" and P.canGrate(S.sel)) and 1 or 0 end
local function curAng() return (S.rot[S.sel] or 0) % P.turns(S.sel) end
local function changed()
  an = P.analyze(S)
  for _, id in ipairs(an.combos) do
    if not P.has(S.found, id) then
      S.found[#S.found + 1] = id
      local q
      for _, c in ipairs(D.COMBOS) do if c.id == id then q = c.q end end
      toast(t(q >= 0 and "k.found" or "k.foundbad", { x = t("combo." .. id) }))
    end
  end
  dirty = true
end

local function addPiece(x, y)
  if math.sqrt(x * x + y * y) > .8 then return false end
  if #S.pieces >= 300 then toast(t("k.full")); return false end
  local mid = P.CENTRED[S.sel] and curCut() == 0
  local lp = S.pieces[#S.pieces]
  if mid and lp and lp.i == S.sel and not lp.g then return false end   -- a drag would pile lobsters up
  if mid then   -- the lobster lands near the middle, at most .25 from it (CENTRE_R in index.html)
    local d = math.sqrt(x * x + y * y)
    if d > .25 then x, y = x * .25 / d, y * .25 / d end
  end
  local piece = { i = S.sel, x = x, y = y, r = math.random() * 6.28, v = math.random(0, 2) }
  if curCut() == 1 then piece.g = 1 elseif P.canRotate(S.sel) then piece.a = curAng() end
  S.pieces[#S.pieces + 1] = piece
  changed()
  return true
end
local function rotatePiece()
  if not P.canRotate(S.sel) then toast(t("k.norotate", { x = P.ingName(S.sel) })); return end
  S.rot[S.sel] = (curAng() + 1) % P.turns(S.sel); dirty = true
end
local function setCut(g)
  if g == 1 and not P.canGrate(S.sel) then toast(t("k.nograte." .. P.noCutKind(S.sel), { x = P.ingName(S.sel) })); return end
  if g == 0 and curCut() == 0 and P.canRotate(S.sel) then rotatePiece(); return end   -- tapping whole again turns the piece
  S.cut = g == 1 and "g" or "w"; dirty = true
end
local function undo()
  if #S.pieces > 0 then S.pieces[#S.pieces] = nil; changed()
  elseif cleared then S.pieces = cleared; cleared = nil; changed() end
end
local function clear()
  if #S.pieces == 0 then return end
  cleared = S.pieces; S.pieces = {}; changed()
end
-- the day and the supplier change every pizza's analysis (topping of the week, supplier's quality and prices)
local function syncWorld()
  P.world.day, P.world.supplier = S.day, S.supplier
  for _, p in ipairs(S.menu) do p.an = nil end
  changed()
end
local function setLang(l)
  P.setLang(l); S.lang = P.lang(); buildCats()
  for _, p in ipairs(S.menu) do p.an = nil end   -- the notes are text in the language
  changed()
end

-- ---------------------------------------------------------------- saving pizzas and the menu
local armed = nil   -- a button pressed once that needs a second press: {what = "new" | "remove", time}
local function arm(what) armed = { what = what, time = 3 } end
local function isArmed(what) return armed and armed.what == what end
local function clampSel() S.msel = math.max(1, math.min(S.msel, #S.menu + 1)) end   -- the row after the last is "+ Create new pizza"
local function freshDraft()
  S.pieces, S.name, S.editing, S.dough, S.sauce = {}, nil, nil, "napo", "tomate"
  cleared = nil; changed()
end
local function newDraft()
  if #S.pieces > 0 and not S.editing and not isArmed("new") then   -- never saved: ask before throwing it away
    arm("new"); toast(t("k.unsaved.title") .. ". " .. t("k.unsaved.new") .. "?"); return
  end
  armed = nil; freshDraft(); S.tab = "kitchen"
end
local function savePizza()
  if #S.pieces < 3 then toast(t("k.needmore")); return end
  local ex
  for k, p in ipairs(S.menu) do if p.id == S.editing then ex = k end end
  local name = S.name
  if not name then   -- no name given: the first combo on it, or "Pizza 4"
    for _, id in ipairs(an.combos) do
      for _, c in ipairs(D.COMBOS) do if c.id == id and c.q > 0 and not name then name = t("combo." .. id) end end
    end
    name = name or ("Pizza " .. (#S.menu + 1))
  end
  local pz = { name = name, dough = S.dough, sauce = S.sauce, pieces = copyPieces(S.pieces) }
  if ex then
    local p = S.menu[ex]
    p.name, p.dough, p.sauce, p.pieces, p.an = pz.name, pz.dough, pz.sauce, pz.pieces, nil
    toast(t("k.updated", { x = name })); S.msel = ex
  else
    pz.id, pz.price = newId(), P.suggestPrice(an.cost)
    S.menu[#S.menu + 1] = pz
    toast(t("k.added", { x = name, p = P.eur(pz.price) })); S.msel = #S.menu
  end
  freshDraft(); S.tab = "menu"   -- saved: the next pizza starts empty, and the Menu shows where it went
end
local function selPizza() return S.menu[S.msel] end
local function editPizza()
  local p = selPizza()
  if not p then newDraft(); return end   -- the "+ Create new pizza" row
  S.dough, S.sauce, S.pieces, S.name, S.editing = p.dough, p.sauce, copyPieces(p.pieces), p.name, p.id
  cleared = nil; S.tab = "kitchen"; changed()
end
local function removePizza()
  local p = selPizza(); if not p then return end
  if not isArmed("remove") then arm("remove"); toast(t("menu.confirm") .. ": " .. p.name .. "?"); return end
  armed = nil
  table.remove(S.menu, S.msel)
  if S.editing == p.id then S.editing = nil end
  clampSel(); dirty = true
end
local function priceStep(d)
  local p = selPizza(); if not p then return end
  p.price = math.max(1, math.min(30, r2(p.price + d))); dirty = true
end
local function pickRow(step) armed = nil; S.msel = S.msel + step; clampSel(); dirty = true end

-- names: the console's keyboard (one textinput with the whole name); on a PC the name is typed in place
local renaming, renameBuf = nil, ""
local function cleanName(s)
  s = s:gsub("[%c|]", ""):gsub("^%s+", ""):gsub("%s+$", "")
  if #s > 40 then s = s:sub(1, 40):gsub("[\192-\255][\128-\191]*$", "") end
  return s
end
local function finishRename(s)
  local set = renaming; renaming = nil
  pcall(love.keyboard.setTextInput, false)
  s = cleanName(s or "")
  if set and s ~= "" then set(s); dirty = true end
end
local function askName(cur, set)
  renaming, renameBuf = set, cur or ""
  if CONSOLE then
    local ok = pcall(love.keyboard.setTextInput, true, { type = "basic", hint = t("k.name"), maxLength = 28 })
    if not ok then pcall(love.keyboard.setTextInput, true) end
  else
    love.keyboard.setTextInput(true)
  end
end
local function renameDraft() askName(S.name or "", function(n) S.name = n end) end
local function renamePizza()
  local p = selPizza(); if not p then return end
  askName(p.name, function(n) p.name = n; if S.editing == p.id then S.name = n end end)
end

-- ---------------------------------------------------------------- drawing helpers
local pages, quads = {}, {}
local fonts = {}
local function hex(h, a)
  local n = tonumber(h:sub(2), 16)
  return { math.floor(n / 65536) / 255, math.floor(n / 256) % 256 / 255, n % 256 / 255, a or 1 }
end
local function col(c, a) love.graphics.setColor(c[1], c[2], c[3], a or c[4] or 1) end
local function spr(key, x, y, alpha, scale)
  local f = A.frames[key]; if not f then return end
  local q = quads[key]
  if not q then q = love.graphics.newQuad(f[2], f[3], f[4], f[5], pages[f[1]]:getDimensions()); quads[key] = q end
  local s = scale or 1
  love.graphics.setColor(1, 1, 1, alpha or 1)
  love.graphics.draw(pages[f[1]], q, math.floor(x - f[4] * s / 2 + .5), math.floor(y - f[5] * s / 2 + .5), 0, s, s)
end
-- icons and bowls: a piece bigger than the box (the whole lobster) is shrunk to fit
local function sprFit(key, x, y, box)
  local f = A.frames[key]; if not f then return end
  spr(key, x, y, nil, math.min(1, box / math.max(f[4], f[5])))
end
-- the letters: a bitmap font at fixed pixel sizes (bfont.lua); fonts[k] keeps the old shape ({f, s}) for getWrap
local BF = require("bfont")
local function mkFont(name)
  return { s = 1, f = { getWrap = function(_, s, w) return 0, BF.wrap(name, s, w) end, getHeight = function() return BF.line(name) end } }
end
local function fw(font, s) return BF.width(font, s) end   -- width in pixels
local function fprint(font, s, x, y) BF.print(font, s, x, y) end
local function text(s, x, y, font, c, align, w)
  col(c)
  if align then BF.printf(font, s, x, y, w, align) else BF.print(font, s, x, y) end
end
local function fitText(s, font, w)   -- cut a line that does not fit, with an ellipsis
  if fw(font, s) <= w then return s end
  while #s > 1 and fw(font, s .. "...") > w do s = s:sub(1, -2):gsub("[\192-\255][\128-\191]*$", "") end
  return s .. "..."
end
local function pxRect(x, y, w, h, c) col(c); love.graphics.rectangle("line", x + .5, y + .5, w - 1, h - 1) end
-- touch buttons: drawn with the bottom screen, and remembered for the next tap
local hits = {}
local function hit(x, y, w, h, fn) hits[#hits + 1] = { x = x, y = y, w = w, h = h, fn = fn } end

local C = {
  ink = hex("#2c1a0b"), bg = hex("#2a170b"), panel = hex("#1a0d05"), cream = hex("#f6e7c8"), gold = hex("#e3b34a"),
  dim = hex("#b39470"), lcd = hex("#8cff73"), good = hex("#8cff73"), bad = hex("#ff7a5c"), combo = hex("#ffd34a"),
}

-- ---------------------------------------------------------------- bottom screen: the bench
local PR = A.pizza / 2
local BW, OY, PX, PY = 320, 22, 6, 34
local PCX, PCY = PX + PR, PY + PR
--[[ the Kitchen's picker, right of the pizza: the groups as tabs in two rows (the topping groups, then dough and
     sauce), and the open group's toppings (or doughs, or sauces) as icons below. S.ktab: the open group;
     S.kfocus: "grid" or "tabs", where the D-pad is. ]]
local KP = { x = 186, ty = 22, tw = 26, gy = 68, cell = 26, cols = 5, cutY = 221, cutMid = 60 }

-- big pieces (a lobster, cheese slices) never poke out past the crust: a circular stencil where it works
local function clipCircle(cx, cy, r)
  return pcall(function()
    love.graphics.stencil(function() love.graphics.circle("fill", cx, cy, r) end, "replace", 1)
    love.graphics.setStencilTest("greater", 0)
  end)
end
local function drawPizza(p, cx, cy)
  spr("sauce_" .. p.sauce, cx, cy)
  local clipped = clipCircle(cx, cy, PR - 1)
  for _, x in ipairs(p.pieces) do spr(P.pieceKey(x), cx + x.x * PR, cy + x.y * PR) end   -- in the order they were put
  if clipped then pcall(love.graphics.setStencilTest) end
  spr("crust_" .. p.dough, cx, cy)
end

local function benchLabel(s, x, y, c, hl)
  local w = fw("tiny", s)
  col(hl or { 1, 1, 1, .55 }); fprint("tiny", s, math.floor(x - w / 2), y + 1)
  col(c or C.ink); fprint("tiny", s, math.floor(x - w / 2), y)
end
-- a gold plate button (like the topping's name plate); returns its right edge
local function plateBtn(label, x, y, fn, w, h, danger)
  h = h or 17
  w = w or math.ceil(fw("tiny", label)) + 12
  col(hex("#4a260f")); love.graphics.rectangle("fill", x, y, w, h)
  col(danger and hex("#e0603c") or C.gold); love.graphics.rectangle("fill", x + 1, y + 1, w - 2, h - 2)
  col(danger and hex("#f59a7c") or hex("#fbe39a")); love.graphics.rectangle("fill", x + 1, y + 1, w - 2, 1)
  benchLabel(label, x + w / 2, y + math.floor((h - 15) / 2) + 1, hex("#3a2706"), danger and hex("#f59a7c", .8) or hex("#fbe39a", .8))
  hit(x, y, w, h, fn)
  return x + w
end
local function nameStrip(name)   -- the pizza's name on the marble strip on top; tap it to rename
  local s = renaming and not CONSOLE and (renameBuf .. "_") or name
  benchLabel(fitText(P.upper(s), "tiny", BW - 8), BW / 2, 6, C.ink, { 1, 1, 1, .4 })
end
local function marble()
  love.graphics.setColor(1, 1, 1)
  spr("marble", BW / 2, 100); spr("marble", BW / 2, 140)
end
local function pizzaOnMarble(p)
  love.graphics.setColor(40 / 255, 30 / 255, 20 / 255, .32)
  love.graphics.ellipse("fill", PCX + 3, PCY + 4, PR + 1, PR)
  drawPizza(p, PCX, PCY)
end

-- the Kitchen's picker: its tabs, and the items of the open one with the key of their icon and whether it is chosen
function KP.tabs() local l = {}; for _, c in ipairs(D.CATS) do l[#l + 1] = c end; l[#l + 1] = "_dough"; l[#l + 1] = "_sauce"; return l end
function KP.open() return S.ktab or catOf(S.sel) end
function KP.items(tab)
  if tab == "_dough" then return D.DOUGH_ORDER end
  if tab == "_sauce" then return D.SAUCE_ORDER end
  return catList[tab]
end
function KP.icon(tab, id)
  if tab == "_dough" then return "crust_" .. id end
  if tab == "_sauce" then return id == "sem" and "crust_" .. S.dough or "sauce_" .. id end
  return P.wholeKey(id, 0, 0)
end
function KP.chosen(tab) return tab == "_dough" and S.dough or tab == "_sauce" and S.sauce or S.sel end
function KP.tabRect(i)   -- 5 tabs on the first row, 4 on the second
  local row, k = i <= 5 and 0 or 1, i <= 5 and i - 1 or i - 6
  return KP.x + k * KP.tw + row * 13, KP.ty + row * 21, KP.tw - 1, 19
end
function KP.cellXY(j) return KP.x + ((j - 1) % KP.cols) * KP.cell, KP.gy + math.floor((j - 1) / KP.cols) * KP.cell end
function KP.choose(tab, id)
  if tab == "_dough" then S.dough = id; changed()
  elseif tab == "_sauce" then S.sauce = id; changed()
  else if id ~= S.sel then S.cut = "w" end; S.sel = id; dirty = true end   -- a new topping starts whole
end
function KP.openTab(tab)
  S.ktab = tab
  if tab:sub(1, 1) ~= "_" and catOf(S.sel) ~= tab then KP.choose(tab, catList[tab][1]) end
end
-- the D-pad: around the icons; up from the first row goes to the tabs, where left/right change group
function KP.button(b)
  local tabs, tab = KP.tabs(), KP.open()
  if S.kfocus == "tabs" then
    if b == "dpleft" or b == "dpright" then KP.openTab(tabs[(idxIn(tabs, tab) - 1 + (b == "dpleft" and -1 or 1)) % #tabs + 1])
    elseif b == "dpdown" then S.kfocus = "grid" end
    return
  end
  local list = KP.items(tab)
  local j = idxIn(list, KP.chosen(tab))
  if b == "dpleft" then j = math.max(1, j - 1)
  elseif b == "dpright" then j = math.min(#list, j + 1)
  elseif b == "dpdown" then j = math.min(#list, j + KP.cols)
  elseif b == "dpup" then if j <= KP.cols then S.kfocus = "tabs"; return end; j = j - KP.cols end
  KP.choose(tab, list[j])
end
function KP.touch(x, y)
  for i, tab in ipairs(KP.tabs()) do
    local tx, ty, tw, th = KP.tabRect(i)
    if x >= tx and x < tx + tw and y >= ty and y < ty + th then KP.openTab(tab); S.kfocus = "grid"; return true end
  end
  local tab = KP.open()
  for j, id in ipairs(KP.items(tab)) do
    local cx, cy = KP.cellXY(j)
    if x >= cx and x < cx + KP.cell and y >= cy and y < cy + KP.cell then KP.choose(tab, id); S.kfocus = "grid"; return true end
  end
  if y >= KP.cutY - 2 and x < 180 then setCut(x < KP.cutMid and 0 or 1); return true end
  return false
end

local function drawKitchenBottom()
  marble()
  pizzaOnMarble(S)
  -- on top: new pizza, add to the menu, the menu; under them the pizza's name (tap it to rename)
  local x = plateBtn(t("k.fresh"), 4, 2, newDraft, nil, 17, isArmed("new"))
  x = plateBtn(t(S.editing and "k.save.edit" or "k.save.new"), x + 5, 2, savePizza, nil, 17)
  plateBtn(t("nav.menu"), x + 5, 2, function() S.tab = "menu"; clampSel(); dirty = true end, nil, 17)
  local s = renaming and not CONSOLE and (renameBuf .. "_") or S.name or t("k.newname")
  benchLabel(fitText(s, "tiny", 176), PCX, 21, C.ink, { 1, 1, 1, .4 })
  hit(PCX - 88, 20, 176, 14, renameDraft)
  -- lower left: whole | chopped, as words
  local sel, cut = S.sel, curCut()
  local labels = { t("bench.whole"), t(P.canGrate(sel) and (P.isCheese(sel) and "bench.grated" or "bench.chopped") or "bench.nograte." .. P.noCutKind(sel)) }
  local cx = 8
  for g = 0, 1 do
    local label, w = labels[g + 1], fw("tiny", labels[g + 1])
    if g == cut then col(hex("#3a2706")); love.graphics.rectangle("fill", cx - 3, KP.cutY - 2, w + 6, 17); col(C.gold)
    else col(g == 1 and not P.canGrate(sel) and hex("#b9a688") or hex("#6c5233")) end
    fprint("tiny", label, cx, KP.cutY)
    cx = cx + w + 6
    if g == 0 then KP.cutMid = cx; col(hex("#6c5233")); fprint("tiny", "|", cx, KP.cutY); cx = cx + 10 end
  end
  -- right: the groups, then the open group's icons
  local tabs, open = KP.tabs(), KP.open()
  for i, tab in ipairs(tabs) do
    local tx, ty, tw, th = KP.tabRect(i)
    local icon = function(a)
      if tab == "_dough" then sprFit("crust_" .. S.dough, tx + tw / 2, ty + th / 2, 15)
      elseif tab == "_sauce" then sprFit(S.sauce == "sem" and "crust_" .. S.dough or "sauce_" .. S.sauce, tx + tw / 2, ty + th / 2, 15)
      else spr("cat_" .. tab, tx + tw / 2, ty + th / 2, a) end
    end
    if tab == open then
      col(hex("#f3e6c6")); love.graphics.rectangle("fill", tx, ty, tw, th); pxRect(tx, ty, tw, th, C.gold); icon()
      if S.kfocus == "tabs" then pxRect(tx - 2, ty - 2, tw + 4, th + 4, { 1, 1, 1 }) end
    else
      col(hex(tab:sub(1, 1) == "_" and "#5a3a1a" or "#7a4520")); love.graphics.rectangle("fill", tx, ty + 1, tw, th - 1); icon(.75)
    end
  end
  col(hex("#4a260f")); love.graphics.rectangle("fill", KP.x - 2, KP.gy - 4, 134, 1)
  local chosen = KP.chosen(open)
  for j, id in ipairs(KP.items(open)) do
    local gx, gy = KP.cellXY(j)
    if gy + KP.cell > 240 then break end
    if id == chosen then
      col(hex("#4a260f")); love.graphics.rectangle("fill", gx, gy, KP.cell, KP.cell)
      pxRect(gx, gy, KP.cell, KP.cell, S.kfocus == "tabs" and C.gold or hex("#ffe08a"))
    else col({ 1, 1, 1, .35 }); love.graphics.rectangle("fill", gx + 1, gy + 1, KP.cell - 2, KP.cell - 2) end
    sprFit(KP.icon(open, id), gx + KP.cell / 2, gy + KP.cell / 2, 21)
  end
end

-- ---------------------------------------------------------------- bottom screen: the chosen menu pizza
local function lcd(x, y, w, rows)
  local h = #rows * 15 + 3
  col(hex("#2a1407")); love.graphics.rectangle("fill", x - 2, y - 2, w + 4, h + 4)
  col(hex("#081008")); love.graphics.rectangle("fill", x, y, w, h)
  for k, r in ipairs(rows) do
    local yy = y + 2 + (k - 1) * 15
    col(C.lcd); fprint("tiny", r[1], x + 3, yy)
    col(r[3] or C.lcd); fprint("tiny", r[2], x + w - 3 - fw("tiny", r[2]), yy)
  end
end
local function drawMenuBottom()
  marble()
  local p = selPizza()
  local strip = function()
    local x = plateBtn(t("nav.cozinha"), 4, 221, function() S.tab = "kitchen"; dirty = true end)
    plateBtn(t("k.fresh"), x + 5, 221, newDraft, nil, nil, isArmed("new"))
  end
  if not p then   -- the "+ Create new pizza" row (or an empty menu)
    if #S.menu == 0 then text(t("menu.empty"), 20, 60, "body", C.ink, "center", 280) end
    plateBtn(t("menu.new", { n = #S.menu }), 60, 130, newDraft, 200, 24)
    strip(); return
  end
  local a = anOf(p)
  pizzaOnMarble(p)
  nameStrip(p.name)
  hit(0, 0, BW, OY, renamePizza)
  -- right column: price with - and +, the figures, edit / rename / remove
  local rx, rw = 186, 130
  plateBtn("-", rx, 26, function() priceStep(-.5) end, 22, 22)
  plateBtn("+", rx + rw - 22, 26, function() priceStep(.5) end, 22, 22)
  text(P.eur(p.price), rx + 22, 28, "body", C.ink, "center", rw - 44)
  local margin = p.price - a.cost
  lcd(rx, 56, rw, {
    { t("k.q"), tostring(a.q), P.qColor(a.q) },
    { l3("kcost"), P.eur(a.cost) },
    { t("menu.margin"), P.eur(margin), margin > 0 and C.good or C.bad },
  })
  plateBtn(t("menu.edit"), rx, 112, editPizza, rw, 19)
  plateBtn(l3("renamel"), rx, 135, renamePizza, rw, 19)
  plateBtn(fitText(t(isArmed("remove") and "menu.confirm" or "menu.remove"), "tiny", rw - 6), rx, 158, removePizza, rw, 19, isArmed("remove"))
  -- who picks it: the share of each customer group that would choose this pizza
  text(fitText(t("menu.who"), "tiny", rw), rx, 181, "tiny", C.ink)
  local W, i = shares(), S.msel
  for j, g in ipairs(D.SEG_ORDER) do
    local x, y, v = rx + ((j - 1) % 2) * 66, 196 + math.floor((j - 1) / 2) * 15, math.floor(W.sh[g][i] * 100 + .5)
    col(hex(D.SEG[g].col), v > 0 and 1 or .4); love.graphics.rectangle("fill", x, y + 4, 7, 7)
    text(t("seg." .. g):sub(1, 3) .. " " .. v .. "%", x + 10, y, "tiny", v > 0 and C.ink or hex("#9a8a70"))
  end
  strip()
end

local drawBottom   -- (defined with the other screens)

-- ---------------------------------------------------------------- top screen: picker and analysis
local function keys(s)   -- the buttons of a screen, one line at the bottom (and START, when it fits)
  local all = s .. "   " .. l3("startopt")
  text(fw("tiny", all) <= 396 and all or s, 0, 224, "tiny", C.dim, "center", 400)
end
local function meter(x, y, w, h, v, c)
  col(hex("#000000", .45)); love.graphics.rectangle("fill", x, y, w, h)
  col(c); love.graphics.rectangle("fill", x, y, math.floor(w * v / 100 + .5), h)
end

local drawHeader
-- the screens, in the order SELECT goes through them, and the header that names them
local TABS = { "kitchen", "menu", "day", "contest", "shop", "city" }
local TAB_KEY = { kitchen = "nav.cozinha", menu = "nav.menu", day = "nav.dia", contest = "nav.concurso", shop = "nav.loja", city = "nav.cidade" }
local function goTab(step)
  if anim or report then return end   -- the day runs to its end, and its report is read first
  local k = (idxIn(TABS, S.tab) - 1 + step) % #TABS + 1
  S.tab = TABS[k]; armed = nil; clampSel(); dirty = true
end
local function stars(r) return string.format(P.lang() == "pt" and "%.1f" or "%.1f", r):gsub("%.", P.lang() == "pt" and "," or ".") .. "*" end
drawHeader = function(alpha)   -- L, the screen before, this screen, the one after, R; then cash and stars
  col(C.panel, alpha); love.graphics.rectangle("fill", 0, 0, 400, 20)
  local i = idxIn(TABS, S.tab)
  local prev, cur, nxt = t(TAB_KEY[TABS[(i - 2) % #TABS + 1]]), t(TAB_KEY[S.tab]), t(TAB_KEY[TABS[i % #TABS + 1]])
  local function key(k, x) col(hex("#4a260f")); love.graphics.rectangle("fill", x, 2, 15, 16); text(k, x, 3, "tiny", C.cream, "center", 15) end
  key("L", 4)
  text(prev, 24, 3, "tiny", C.dim)
  local x = 24 + fw("tiny", prev) + 9
  text(cur, x, 2, "body", C.gold)
  x = x + fw("body", cur) + 9
  text(nxt, x, 3, "tiny", C.dim)
  key("R", x + fw("tiny", nxt) + 6)
  text(P.eur(S.money) .. "  " .. stars(S.rep), 200, 2, "body", S.money < 0 and C.bad or C.cream, "right", 194)
end

local function drawTop()
  col(C.bg); love.graphics.rectangle("fill", 0, 0, 400, 240)
  drawHeader()
  -- left: the chosen topping (its picture, price and weight a portion, who loves it, its combos)
  local id = S.sel
  col(C.panel); love.graphics.rectangle("fill", 4, 24, 194, 74)
  col(hex("#f3e6c6")); love.graphics.rectangle("fill", 8, 28, 46, 46); pxRect(8, 28, 46, 46, C.gold)
  sprFit(P.wholeKey(id, 0, curAng()), 31, 51, 40)
  text(fitText(P.ingName(id), "body", 138), 60, 28, "body", C.cream)
  local cutL = curCut() == 1 and t(P.isCheese(id) and "bench.grated" or "bench.chopped") or t("bench.whole")
  text(fitText(P.eur(P.ingC(id)) .. " · " .. P.fmtG(P.pieceGrams({ i = id, g = curCut() == 1 or nil })) .. " · " .. cutL, "small", 136), 60, 47, "small", C.dim)
  local wk = P.week()
  local fan = P.has(D.CASA, id) and t("seg.estudante") or P.has(D.EXOTIC, id) and t("seg.turista") or nil
  if wk.ing == id then text(l3("kweek"), 60, 62, "small", C.good)
  elseif wk.low == id then text(l3("klow"), 60, 62, "small", C.bad)
  elseif fan then text("♥ " .. fan, 60, 62, "small", C.good) end
  local cs = {}
  for _, c in ipairs(D.COMBOS) do for _, r in ipairs(c.req) do if r == id then cs[#cs + 1] = t("combo." .. c.id); break end end end
  if #cs > 0 then text(fitText(l3("kcombo") .. ": " .. table.concat(cs, ", "), "small", 186), 8, 79, "small", C.combo) end
  -- dough, sauce, the notes
  col(C.panel); love.graphics.rectangle("fill", 4, 102, 194, 38)
  text(t("dough." .. S.dough), 10, 105, "small", C.cream); text(t("k.dough"), 10, 105, "small", C.dim, "right", 182)
  text(t("sauce." .. S.sauce), 10, 121, "small", C.cream); text(t("k.sauce"), 10, 121, "small", C.dim, "right", 182)
  local y = 146
  if an.n == 0 then text(t("k.empty"), 6, y, "small", C.dim, "left", 190)
  else
    for i = 1, math.min(4, #an.notes) do
      local nt = an.notes[i]
      text(fitText(nt[2], "small", 190), 6, y, "small", nt[1] == "good" and C.good or nt[1] == "combo" and C.combo or C.bad)
      y = y + 17
    end
  end
  -- right: quality, cost, suggested price, appeal
  local rx = 208
  col(C.panel); love.graphics.rectangle("fill", rx - 4, 24, 192, 196)
  local qc = P.qColor(an.q)
  text(t("k.q"), rx, 27, "small", C.dim)
  text(tostring(an.q), rx, 42, "big", qc)
  meter(rx + 56, 54, 124, 8, an.q, qc)
  text(l3("kcost"), rx, 80, "small", C.dim); text(P.eur(an.cost), rx, 78, "body", C.cream, "right", 180)
  text(l3("ksugg"), rx, 98, "small", C.dim); text(P.eur(P.suggestPrice(an.cost)), rx, 96, "body", C.cream, "right", 180)
  text(l3("kappeal"), rx, 122, "small", C.dim)
  for i, sk in ipairs(D.SEG_ORDER) do
    local yy = 140 + (i - 1) * 19
    text(fitText(t("seg." .. sk), "small", 76), rx, yy, "small", C.cream)
    meter(rx + 80, yy + 5, 72, 8, an.appeal[sk], hex(D.SEG[sk].col))
    text(tostring(an.appeal[sk]), rx, yy, "small", C.cream, "right", 180)
  end
  keys(l3("keys1"))
end

-- a menu pizza drawn small (the whole 170 px pizza scaled)
local function miniPizza(p, cx, cy, size)
  love.graphics.push(); love.graphics.translate(cx, cy); love.graphics.scale(size / A.pizza)
  drawPizza(p, 0, 0)
  love.graphics.pop()
end
local ROW_H, ROWS = 37, 5
local function drawMenuTop()
  col(C.bg); love.graphics.rectangle("fill", 0, 0, 400, 240)
  drawHeader()
  local sp = selPizza()
  local loss = sp and sp.price < anOf(sp).cost
  local lead = t("menu.house") .. " (" .. #S.menu .. ")  ·  " .. t("k.book", { n = #S.found, t = #D.COMBOS })
  local why = sp and not loss and G.menuWhy(S, shares(), S.msel)   -- why it is not the first choice of the group it suits best
  if why then text(fitText(why, "tiny", 388), 6, 23, "tiny", C.combo)
  else text(fitText(loss and t("menu.loss", { x = P.eur(anOf(sp).cost - sp.price) }) or lead, "small", 388), 6, 21, "small", loss and C.bad or C.dim) end
  local n = #S.menu + 1
  local first = math.max(1, math.min(S.msel - 2, n - ROWS + 1))
  for row = 0, ROWS - 1 do
    local k = first + row
    if k > n then break end
    local y = 37 + row * ROW_H
    local on = k == S.msel
    col(on and hex("#4a260f") or C.panel); love.graphics.rectangle("fill", 6, y, 388, ROW_H - 3)
    if on then pxRect(5, y - 1, 390, ROW_H - 1, C.gold) end
    local p = S.menu[k]
    if p then
      local a = anOf(p)
      miniPizza(p, 24, y + 15, 28)
      text(fitText(p.name, "body", 220), 44, y + 1, "body", C.cream)
      text(fitText(t("dough." .. p.dough) .. " · " .. t("sauce." .. p.sauce), "tiny", 200), 44, y + 18, "tiny", C.dim)
      text(P.eur(p.price), 250, y + 1, "body", C.gold, "right", 138)
      local margin = p.price - a.cost
      text("Q" .. a.q, 252, y + 18, "tiny", P.qColor(a.q))
      text(t("menu.margin") .. " " .. P.eur(margin), 280, y + 18, "tiny", margin > 0 and C.good or C.bad, "right", 108)
    else
      text(t("menu.new", { n = #S.menu }), 6, y + 8, "body", on and C.gold or C.dim, "center", 388)
    end
  end
  keys(l3("mkeys1"))
end

local function drawToast()
  if toasts[1] then
    local s = toasts[1].s
    local w = math.min(380, fw("body", s) + 16)
    col(hex("#000000", .85)); love.graphics.rectangle("fill", 200 - w / 2, 213, w, 24)
    pxRect(200 - w / 2, 213, w, 24, C.gold)
    text(fitText(s, "body", w - 8), 200 - w / 2, 217, "body", C.combo, "center", w)
  end
end
local drawTopScreen

-- ---------------------------------------------------------------- the day: open the doors, the street, the report
local SALA = require("sala")   -- the dining room on the touch screen (as the browser's day)
local idleScene   -- the room before the doors open: the staff in their places
local function startDay()
  if anim or report then return end
  if #S.menu == 0 then toast(t("ct.need")); return end
  local RS = G.roomStats(S)
  if RS.seats == 0 then toast(t("rm.noseats")); return end
  if not RS.kitchenOk then toast(t("rm.w.kitchen")); return end
  syncWorld(); histOn = false; idleScene = nil
  anim = { res = G.simulateDay(S), t = 0, speed = 1, idx = 1, cnt = { served = 0, rival = 0, left = 0, rev = 0 }, faces = { good = 0, meh = 0, bad = 0 }, bubbles = {}, sc = SALA.scene(S, G) }
end
local function endDay()
  local a = anim
  anim = nil
  report = G.finishDay(S, a.res)
  syncWorld(); save()
end
local function updateDay(dt)
  local a = anim
  if a.paused then return end
  local k = SALA.pace(a, D.DAY_SECONDS)
  -- small steps, so a fast day does not jump through walls
  local left = math.min(dt, .1) * a.speed * k
  while left > 0 do
    local d = math.min(left, .05); left = left - d
    if SALA.step(a, d, S, D.DAY_SECONDS, P.eur, C) then endDay(); return end
  end
end
local function skipDay()
  if not anim then return end
  while anim.res.events[anim.idx] do anim.idx = anim.idx + 1 end
  endDay()
end

local function lcdRows()
  local a = anim
  local c = a and a.cnt or { served = 0, rival = 0, left = 0, rev = 0 }
  local m = a and math.min(a.t / D.DAY_SECONDS, 1) * 11 * 60 or 0
  local clock = string.format("%02d:%02d", 12 + math.floor(m / 60), math.floor(m % 60 / 15) * 15)
  local rep = string.format("%.1f", S.rep); if P.lang() == "pt" then rep = rep:gsub("%.", ",") end
  return {
    { t("lcd.day") .. " " .. S.day .. " " .. P.upper(G.weekday(S.day)), clock },
    { t("lcd.pop"), rep .. "/5" },
    { a and t("lcd.street") or t("lcd.exp"), a and tostring(#a.res.events - a.idx + 1 + #a.sc.people) or ("~" .. G.expected(S)) },
    { t("lcd.served"), tostring(c.served) },
    { t("lcd.rival"), tostring(c.rival) },
    { t("lcd.left"), tostring(c.left) },
    false,
    { t("lcd.cooks"), tostring(#G.crew(S, "cook")) },
    { t("lcd.waiters"), tostring(#G.crew(S, "waiter")) },
    { t("lcd.cap"), c.served .. "/" .. math.min(G.capacity(S), G.serviceCap(S)) },
    false,
    { t("lcd.rev"), P.eur(c.rev) },
    { t("lcd.cash"), P.eur(S.money) },
  }
end

-- the sales history (as Menu › Sales history in the browser game): totals, profit by day, the last days
local function drawHistTop()
  col(C.bg); love.graphics.rectangle("fill", 0, 0, 400, 240)
  drawHeader()
  local H = S.hist
  text(t("hist.title"), 8, 22, "small", C.gold)
  if #H == 0 then
    text(t("hist.none"), 8, 44, "small", C.cream, "left", 384)
  else
    local served, takings, profit, best = 0, 0, 0, H[1]
    for _, h in ipairs(H) do served = served + h.n; takings = takings + h.v; profit = profit + h.p; if h.p > best.p then best = h end end
    local sum = {
      { t("hist.sum.days"), tostring(#H) }, { t("hist.sum.served"), tostring(served) }, { t("hist.sum.takings"), P.eur(takings) },
      { t("hist.sum.profit"), P.eur(profit) }, { t("hist.sum.avg"), P.eur(profit / #H) }, { t("hist.sum.best"), t("hist.day") .. " " .. best.d .. " · " .. P.eur(best.p) },
    }
    for k, x in ipairs(sum) do
      local cx, cy = 8 + ((k - 1) % 3) * 130, 38 + math.floor((k - 1) / 3) * 30
      text(fitText(x[1], "tiny", 124), cx, cy, "tiny", C.dim); text(fitText(x[2], "small", 124), cx, cy + 13, "small", C.cream)
    end
    -- profit by day: the last 30 days, a bar each, green above the line, red below
    text(t("hist.chart"), 8, 98, "tiny", C.dim)
    local from = math.max(1, #H - 29)
    local mx = 1
    for k = from, #H do mx = math.max(mx, math.abs(H[k].p)) end
    local x0, y0, bw, hh = 8, 140, math.floor(384 / 30), 24
    col(C.dim, .5); love.graphics.rectangle("fill", x0, y0, 384, 1)
    for k = from, #H do
      local h = math.floor(math.abs(H[k].p) / mx * hh + .5)
      col(H[k].p >= 0 and C.good or C.bad)
      love.graphics.rectangle("fill", x0 + (k - from) * bw, H[k].p >= 0 and y0 - h or y0 + 1, bw - 2, h)
    end
    -- how they left, over the kept days (days before the faces have none)
    local tot, any = { 0, 0, 0 }, false
    for _, h in ipairs(H) do if h.f then any = true; for i = 1, 3 do tot[i] = tot[i] + h.f[i] end end end
    if any then
      local all = math.max(1, tot[1] + tot[2] + tot[3])
      local x = 8
      text(t("face.title"), x, 146, "tiny", C.dim); x = x + fw("tiny", t("face.title")) + 10
      for k, key in ipairs({ "good", "meh", "bad" }) do
        SALA.face(key, x + 5, 146)
        local s = math.floor(tot[k] / all * 100 + .5) .. "% " .. t("face." .. key)
        text(s, x + 13, 146, "tiny", C.cream); x = x + 13 + fw("tiny", s) + 12
      end
    end
    -- day by day, the newest first
    local cols = { 8, 60, 120, 190 }
    local y = 164
    for k, s2 in ipairs({ t("hist.day"), t("hist.served"), t("hist.profit"), t("hist.top") }) do text(s2, cols[k], y, "tiny", C.dim) end
    for k = #H, math.max(1, #H - 2), -1 do
      local h = H[k]
      y = y + 14
      text(tostring(h.d), cols[1], y, "tiny", C.cream); text(h.n .. "/" .. h.N, cols[2], y, "tiny", C.cream)
      text(P.eur(h.p), cols[3], y, "tiny", h.p >= 0 and C.good or C.bad)
      text(fitText(h.top ~= "" and (h.top .. " ×" .. h.topN) or "—", "tiny", 200), cols[4], y, "tiny", C.cream)
    end
  end
  keys(l3("hback"))
end

-- the day: the dining room on the top screen (sala.lua, 320 wide, centred), with the clock and the takings on the
-- left and how customers left on the right; the LCD, the news and the buttons on the touch screen
local function drawDayTop()
  col(C.bg); love.graphics.rectangle("fill", 0, 0, 400, 240)
  if not anim and not idleScene then idleScene = SALA.scene(S, G) end
  love.graphics.push(); love.graphics.translate(40, 0)
  SALA.draw(anim, anim and anim.sc or idleScene, S)
  local lbl = P.upper(S.rival.name) .. " >"
  local w = fw("tiny", lbl) + 8
  col(hex("#120a04", .75)); love.graphics.rectangle("fill", 316 - w, 223, w, 16)
  text(lbl, 316 - w, 224, "tiny", hex("#ffcf4a"), "center", w)
  if anim then
    for _, b in ipairs(anim.bubbles) do
      local bw = fw("tiny", b.s) + 6
      local x = math.max(2, math.min(318 - bw, b.x - bw / 2))
      col(hex("#000000", .7)); love.graphics.rectangle("fill", x, math.max(22, b.y), bw, 16)
      text(b.s, x, math.max(22, b.y) + 1, "tiny", b.c, "center", bw)
    end
    if anim.paused then
      local s = P.upper(t("run.pause"))
      local pw = fw("small", s) + 16
      col(hex("#120a04", .8)); love.graphics.rectangle("fill", 160 - pw / 2, 108, pw, 24)
      text(s, 160 - pw / 2, 112, "small", C.gold, "center", pw)
    end
  end
  love.graphics.pop()
  -- the side strips: day and clock, takings; the faces so far
  local rows = lcdRows()
  col(hex("#2a1407")); love.graphics.rectangle("fill", 0, 20, 40, 220); love.graphics.rectangle("fill", 360, 20, 40, 220)
  text(t("lcd.day"), 0, 28, "tiny", C.dim, "center", 40)
  text(tostring(S.day), 0, 42, "body", C.cream, "center", 40)
  text(rows[1][2], 0, 64, "tiny", C.lcd, "center", 40)
  if anim then
    text("$", 0, 90, "tiny", C.dim, "center", 40)
    text(fitText(P.eur(anim.cnt.rev):gsub("%.%d+$", ""), "tiny", 38), 0, 104, "tiny", C.good, "center", 40)
    for k, key in ipairs({ "good", "meh", "bad" }) do
      local y = 34 + (k - 1) * 34
      SALA.face(key, 380, y)
      text(tostring(anim.faces[key]), 360, y + 12, "tiny", C.cream, "center", 40)
    end
  end
  drawHeader(.85)   -- see-through over the back wall
end
local function drawDayBottom()
  col(C.bg); love.graphics.rectangle("fill", 0, 0, 320, 240)
  -- the LCD
  col(hex("#2a1407")); love.graphics.rectangle("fill", 2, 2, 156, 172)
  col(hex("#081008")); love.graphics.rectangle("fill", 4, 4, 152, 168)
  local y = 6
  for _, r in ipairs(lcdRows()) do
    if r then
      text(fitText(r[1], "tiny", 146 - fw("tiny", r[2]) - 6), 7, y, "tiny", C.lcd)
      text(r[2], 7, y, "tiny", C.lcd, "right", 146)
      y = y + 13
    else
      col(C.lcd, .35); love.graphics.rectangle("fill", 7, y + 5, 146, 1); y = y + 9
    end
  end
  -- right: contest today, news, the manager's notes
  local x, w = 164, 152
  y = 2
  if S.day % 5 == 0 then
    local entry
    for _, p in ipairs(S.menu) do if p.id == S.contestEntry then entry = p end end
    local s = "> " .. t("day.ban", { x = t("th." .. G.themeFor(S.day)) }) .. " " ..
      (entry and t("day.ban.in", { p = entry.name }) or t("day.ban.none"))
    local F = fonts.tiny
    local _, wr = F.f:getWrap(s, (w - 4) / F.s)
    local h = #wr * F.f:getHeight() * F.s + 4
    col(hex("#4a260f")); love.graphics.rectangle("fill", x - 2, y, w + 4, h)
    text(s, x + 2, y + 2, "tiny", C.combo, "left", w - 4)
    y = y + h + 4
  end
  text(t("day.news"), x, y, "small", C.gold); y = y + 15
  local notes = {}
  if G.roomStats(S).seats * 3 < G.expected(S) then notes[#notes + 1] = t("day.seats") end
  if math.min(G.capacity(S), G.serviceCap(S)) < G.expected(S) * .6 then notes[#notes + 1] = t("day.queue") end
  local lines = {}
  for _, n in ipairs(S.news) do lines[#lines + 1] = { G.newsText(n), C.cream } end
  for _, n in ipairs(notes) do table.insert(lines, 1, { t("day.warn") .. ": " .. n, C.bad }) end
  local F = fonts.tiny
  for _, l in ipairs(lines) do
    local _, wrapped = F.f:getWrap(l[1], (w - 4) / F.s)
    local h = #wrapped * F.f:getHeight() * F.s
    if y + h > 180 then break end
    text(l[1], x, y, "tiny", l[2], "left", w - 4)
    y = y + h + 3
  end
  text(anim and l3("drun") or (l3("dkeys") .. "   " .. l3("hkeys")), 0, 186, "tiny", C.dim, "center", 320)
  if anim then
    local bx = 6
    bx = plateBtn(t(anim.paused and "run.resume" or "run.pause"), bx, 206, function() anim.paused = not anim.paused end, nil, 26, anim.paused) + 6
    for _, v in ipairs({ 1, 2, 4 }) do   -- a speed button also resumes
      bx = plateBtn("x" .. v, bx, 206, function() anim.speed = v; anim.paused = false end, 34, 26, anim.speed == v and not anim.paused) + 6
    end
    plateBtn(fitText(t("run.skip"), "tiny", 310 - bx), bx, 206, skipDay, 314 - bx, 26)
  else
    plateBtn(fitText(t("day.open", { d = S.day }), "tiny", 300), 20, 206, startDay, 280, 26)
  end
end

-- the close of the day
local function drawReportTop()
  col(C.bg); love.graphics.rectangle("fill", 0, 0, 400, 240)
  drawHeader()
  local r, res = report, report.res
  local net = r2(r.profit - (r.interest or 0))   -- the day's result after the bank's interest
  text(t(net >= 0 and "rep.good" or "rep.bad") .. ": " .. P.eur(net), 8, 23, "body", net >= 0 and C.good or C.bad)
  text(t("rep.close", { d = r.day, w = G.weekday(r.day) }), 8, 25, "small", C.dim, "right", 384)
  local rows = {
    { t("rep.served"), t("rep.ofN", { n = res.served, N = res.N }) },
    { t("rep.rival", { x = S.rival.name }), tostring(res.toRival) },
    { t("rep.full"), tostring(res.full) },
    { t("rep.noseat"), tostring(res.noseat) },
  }
  local money = {
    { t("rep.revenue"), P.eur(res.revenue) },
    { t("rep.ing"), P.eur(-res.ingCost) },
    { t("rep.rent"), P.eur(-r.rent) },
    { t("rep.sal"), P.eur(-r.sal) },
  }
  if (r.interest or 0) > 0 then money[#money + 1] = { t("rep.interest"), P.eur(-r.interest) } end
  money[#money + 1] = { t("rep.result"), P.eur(net), net >= 0 and C.good or C.bad }
  for k, row in ipairs(rows) do
    local y = 46 + (k - 1) * 16
    text(fitText(row[1], "small", 180 - fw("small", row[2])), 8, y, "small", C.cream); text(row[2], 8, y, "small", C.cream, "right", 186)
  end
  for k, row in ipairs(money) do
    local y = 46 + (k - 1) * (#money > 5 and 14 or 16)
    text(row[1], 208, y, "small", row[3] or C.cream); text(row[2], 208, y, "small", row[3] or C.cream, "right", 186)
  end
  -- how they left: the three faces with their counts, and why the unhappy ones were (as facesHTML() in index.html)
  local fc = { res.happy, res.meh or 0, (res.sad or 0) + res.full + res.noseat + (res.nostock or 0) }
  local x = 8
  text(t("face.title"), x, 146, "tiny", C.dim)
  x = x + fw("tiny", t("face.title")) + 10
  for k, key in ipairs({ "good", "meh", "bad" }) do
    SALA.face(key, x + 5, 146)
    local s = fc[k] .. " " .. t("face." .. key)
    text(s, x + 13, 146, "tiny", C.cream); x = x + 13 + fw("tiny", s) + 12
  end
  if fc[3] > 0 then text(fitText(t("face.why", { f = res.sad or 0, g = fc[3] - (res.sad or 0) }), "tiny", 384), 8, 161, "tiny", C.dim) end
  local f = function(v) local s = string.format("%.2f", v); return P.lang() == "pt" and s:gsub("%.", ",") or s end
  text(t("rep.rep") .. ": " .. f(r.repBefore) .. " -> " .. f(r.repAfter) .. "*", 8, 176, "small", C.gold)
  local w = P.week(S.day)   -- the week, short: no reasons in brackets
  local wk = (t("wk.ing", { x = P.ingName(w.ing) }) .. "  " .. t("wk.low", { x = P.ingName(w.low) }) .. "  " ..
    t("wk.combo", { x = t("combo." .. w.combo), r = "" })):gsub("%s*%(.-%)", "")
  col(hex("#4a260f")); love.graphics.rectangle("fill", 6, 192, 388, 32)
  text(wk, 10, 193, "tiny", C.combo, "left", 380)
  keys(l3("rkeys"))
end
local function closeReport()
  if report and report.res and S.over then report = { over = true }; return end
  report = nil
  if S.over then S.over = false; freshGame(); starterMenu(); S.found = {}; freshDraft(); syncWorld(); S.tab = "kitchen" end
end
local function drawReportBottom()
  col(hex("#f3ead3")); love.graphics.rectangle("fill", 0, 0, 320, 240)
  local r = report
  if r.over then
    text(t("end.title"), 10, 30, "big", C.bad, "center", 300)
    text(t("end.lead", { d = S.day - 1 }), 20, 80, "body", C.ink, "center", 280)
    plateBtn(t("end.again"), 60, 180, closeReport, 200, 26)
    return
  end
  local y = 6
  if r.goal then
    text(t("goal.title") .. " " .. t("goal.lead", { m = P.eur(S.money), r = string.format("%.1f", S.rep), d = r.day }), 8, y, "tiny", hex("#1f7a3a"), "left", 304)
    y = y + 34
  end
  -- with several shops: how each did today (the open one first) and the day's total
  if r.others and #r.others > 0 then
    text(t("rep.shops"), 8, y, "tiny", C.ink); text(t("rep.n"), 200, y, "tiny", C.ink, "right", 50); text(t("rep.result"), 250, y, "tiny", C.ink, "right", 60)
    y = y + 14
    local rows = { { name = G.shopName(S), open = true, served = r.res.served, N = r.res.N, profit = r.profit } }
    for _, x in ipairs(r.others) do rows[#rows + 1] = x end
    local tot = 0
    for _, x in ipairs(rows) do
      tot = tot + x.profit
      text(fitText(x.name .. (x.open and "" or (" · " .. t("rep.closed"))), "tiny", 190), 8, y, "tiny", C.ink)
      text(x.open and (x.served .. "/" .. x.N) or "-", 200, y, "tiny", C.ink, "right", 50)
      text(P.eur(x.profit), 250, y, "tiny", x.profit >= 0 and hex("#1f7a3a") or C.bad, "right", 60)
      y = y + 14
    end
    text(t("rep.total"), 8, y, "tiny", C.ink); text(P.eur(r2(tot - (r.interest or 0))), 250, y, "tiny", C.ink, "right", 60)
    y = y + 17
  end
  -- who bought what: each pizza sold, by customer group
  local bs = r.res and r.res.bySeg
  if bs and next(bs) then
    text(t("rep.byseg"), 8, y, "tiny", C.ink)
    for j, g in ipairs(D.SEG_ORDER) do text(t("seg." .. g):sub(1, 3), 160 + (j - 1) * 38, y, "tiny", hex(D.SEG[g].col), "right", 34) end
    y = y + 15
    for _, p in ipairs(S.menu) do
      local any = false
      for _, g in ipairs(D.SEG_ORDER) do if (bs[g] or {})[p.id] then any = true end end
      if any then
        text(fitText(p.name, "tiny", 148), 8, y, "tiny", C.ink)
        for j, g in ipairs(D.SEG_ORDER) do text(tostring((bs[g] or {})[p.id] or 0), 160 + (j - 1) * 38, y, "tiny", C.ink, "right", 34) end
        y = y + 14
      end
    end
    y = y + 4
  end
  local F = fonts.tiny
  for _, q in ipairs(r.quotes) do
    if y > 150 then break end   -- leave room for the contest and the button
    local s = t("seg." .. q[1]) .. ": “" .. q[2] .. "”"
    local _, wrapped = F.f:getWrap(s, 304 / F.s)
    text(s, 8, y, "tiny", C.ink, "left", 304)
    y = y + #wrapped * F.f:getHeight() * F.s + 4
  end
  local c = r.contest
  if c then
    y = y + 2
    text(t("ct.res", { t = t("th." .. c.th), n = c.pos }) .. (c.prize > 0 and (" · +" .. P.eur(c.prize)) or ""), 8, y, "small", hex("#8a5a00")); y = y + 16
    if c.dq then text(t("ct.dq", { x = c.dq }), 8, y, "tiny", C.bad); y = y + 14 end
    for k, x in ipairs(c.rows) do
      local cc = x.me and hex("#8a5a00") or C.ink
      if y > 190 then break end
      text(k .. ". " .. fitText(x.n, "tiny", 250), 12, y, "tiny", cc); text(tostring(x.s), 12, y, "tiny", cc, "right", 296); y = y + 14
    end
  end
  local res = r.res
  local tip = res.noseat > 3 and "rep.tip.seats" or res.full > 3 and "rep.tip.queue" or res.toRival > res.served and "rep.tip.rival" or nil
  if tip and y < 170 then text(t(tip), 8, math.max(y + 2, 170), "tiny", hex("#6c5233"), "left", 304) end
  plateBtn(t("rep.go"), 90, 210, closeReport, 140, 26)
end

-- ---------------------------------------------------------------- the contest
local function enterContest(p)
  if not S.contestEntry then
    if S.money < D.ENTRY_FEE then toast(t("ts.nofee")); return end
    S.money = S.money - D.ENTRY_FEE
  end
  S.contestEntry = p.id; toast(t("ts.entered")); dirty = true
end
local function drawContestTop()
  col(C.bg); love.graphics.rectangle("fill", 0, 0, 400, 240)
  drawHeader()
  local cd = G.nextContestDay(S)
  local th, left = G.themeFor(cd), cd - S.day
  local when = left == 0 and t("ct.today") or left == 1 and t("ct.tomorrow") or t("ct.in", { n = left })
  text(when .. " · " .. t("ct.day", { d = cd }) .. " (" .. G.weekday(cd) .. ")", 8, 22, "small", C.dim)
  text(t("th." .. th), 8, 36, "body", C.gold)
  text(t("th." .. th .. ".d"), 8, 54, "small", C.cream, "left", 384)
  local base = math.floor(math.min(92, 50 + cd * 1.1) + .5)
  local rows = {}
  for k, pr in ipairs({ { 600, .4 }, { 250, .2 }, { 80, .1 } }) do
    local r = tostring(pr[2]); if P.lang() == "pt" then r = r:gsub("%.", ",") end
    rows[#rows + 1] = { t("ct.p" .. k), (t("ct.and", { m = "$" .. pr[1], r = r }):gsub("★", "*")) }
  end
  rows[#rows + 1] = { t("ct.fee"), "$" .. D.ENTRY_FEE }
  rows[#rows + 1] = { t("ct.rivals"), t("ct.pts", { a = base - 8, b = base + 8 }) }
  col(C.panel); love.graphics.rectangle("fill", 6, 92, 192, 84)
  for k, r in ipairs(rows) do
    local y = 95 + (k - 1) * 16
    text(fitText(r[1], "small", 178 - fw("small", r[2])), 10, y, "small", C.dim); text(r[2], 10, y, "small", C.cream, "right", 184)
  end
  col(C.panel); love.graphics.rectangle("fill", 202, 92, 192, 128)
  text(t("ct.hist"), 206, 95, "small", C.gold)
  if #S.contestLog == 0 then text(t("ct.none"), 206, 113, "tiny", C.dim, "left", 184) end
  for k, l in ipairs(S.contestLog) do
    if k > 3 then break end
    local y = 113 + (k - 1) * 34
    text(fitText(t("ct.histrow", { d = l.day, t = t("th." .. l.theme) }), "tiny", 184), 206, y, "tiny", C.cream)
    text(fitText(l.pizza, "tiny", 100), 206, y + 15, "tiny", C.dim)
    text(t("ct.place", { n = l.pos }) .. (l.prize > 0 and (" · " .. P.eur(l.prize)) or ""), 206, y + 15, "tiny", C.combo, "right", 184)
  end
  text(t("ct.judge", { d = cd }), 8, 182, "tiny", C.dim, "left", 190)
  keys(l3("ckeys"))
end
local function drawContestBottom()
  col(hex("#f3ead3")); love.graphics.rectangle("fill", 0, 0, 320, 240)
  text(t("ct.pick"), 8, 4, "small", C.ink)
  text(fitText(t(S.contestEntry and "ct.swap" or "ct.pay"), "tiny", 304), 8, 21, "tiny", hex("#6c5233"))
  if #S.menu == 0 then text(t("ct.need"), 8, 60, "body", C.ink, "center", 304); return end
  S.csel = math.max(1, math.min(S.csel, #S.menu))
  local th = G.themeFor(G.nextContestDay(S))
  local RH, N = 35, 5
  local first = math.max(1, math.min(S.csel - 2, #S.menu - N + 1))
  for row = 0, N - 1 do
    local k = first + row
    local p = S.menu[k]
    if not p then break end
    local y = 40 + row * RH
    local on, entered = k == S.csel, p.id == S.contestEntry
    col(entered and hex("#e3b34a") or on and hex("#eadcb8") or hex("#f9f3e3")); love.graphics.rectangle("fill", 6, y, 308, RH - 3)
    if on then pxRect(5, y - 1, 310, RH - 1, hex("#4a260f")) end
    miniPizza(p, 22, y + 15, 26)
    local sc = P.contestScore(th, p)
    text(fitText((entered and "> " or "") .. p.name, "small", 260), 42, y + 1, "small", C.ink)
    text(fitText(sc.dq and t("ct.dq", { x = sc.dq }) or t("ct.pre", { n = math.floor(sc.s + .5) }), "tiny", 260), 42, y + 16, "tiny", sc.dq and hex("#b0381c") or hex("#6c5233"))
    hit(6, y, 308, RH - 3, function() S.csel = k; enterContest(p) end)
  end
end

-- ---------------------------------------------------------------- the shop
local SHOP_ROWS = { "oven", "team", "hire", "room", "ads", "supplier", "study", "bank", "reset" }
local function shopItem(id) for _, it in ipairs(G.SHOP) do if it.id == id then return it end end end
local function buyItem(it)
  if not it.ok(S) then return end
  local c = it.cost(S)
  if S.money < c then return end
  S.money = S.money - c; it.buy(S); toast(t("ts.bought", { x = t("shop." .. it.id) })); dirty = true
end
local function setSupplier(k) S.supplier = k; syncWorld() end
local function runStudy()
  if S.studyWeek == G.weekOf(S.day) or S.money < D.STUDY_COST then return end
  S.money = S.money - D.STUDY_COST; S.studyWeek = G.weekOf(S.day)
  table.insert(S.tips, 1, G.studyTips(S))
  while #S.tips > 6 do table.remove(S.tips) end
  dirty = true
end
local function resetGame()
  if not isArmed("reset") then arm("reset"); toast(t("ts.sure")); return end
  armed = nil
  freshGame(); starterMenu(); S.found = {}; freshDraft(); syncWorld(); S.tab = "kitchen"
  toast(t("ts.reset"))
end
local function shopAction(id)
  local it = shopItem(id)
  if it then buyItem(it)
  elseif id == "supplier" then setSupplier(S.supplier % 3 + 1)
  elseif id == "study" then runStudy()
  elseif id == "room" then openEditor()
  elseif id == "reset" then resetGame() end
end
local function shopRow(id)   -- name, state, price
  local it = shopItem(id)
  if it then return t("shop." .. id), it.lvl(S), it.ok(S) and P.eur(it.cost(S)) or t("shop.done") end
  if id == "supplier" then return t("sup.title"), t("sup." .. S.supplier), "" end
  if id == "study" then return t("study.title"), S.studyWeek == G.weekOf(S.day) and t("study.done") or "", P.eur(D.STUDY_COST) end
  if id == "team" then return t("staff.title"), t("staff.pay", { w = P.eur(G.wages(S)) }), "" end
  if id == "hire" then return t("staff.cands"), "", P.eur(D.HIRE_COST) end
  if id == "bank" then return t("bank.title"), t("bank.owe") .. " " .. P.eur(S.loan or 0), "" end
  if id == "room" then
    local A = G.roomStats(S)
    return l3("edroom"), t("rm.seats", { n = A.seats }) .. (A.nblocked > 0 and ("  ·  X " .. A.nblocked) or ""), ""
  end
  return t("shop.reset"), "", ""
end
local function drawShopTop()
  col(C.bg); love.graphics.rectangle("fill", 0, 0, 400, 240)
  drawHeader()
  text(fitText(t("shop.lead", { m = P.eur(S.money) }), "small", 388), 6, 21, "small", C.dim)
  S.ssel = math.max(1, math.min(S.ssel, #SHOP_ROWS))
  for k, id in ipairs(SHOP_ROWS) do
    local y = 39 + (k - 1) * 20
    local on = k == S.ssel
    col(on and hex("#4a260f") or C.panel); love.graphics.rectangle("fill", 6, y, 388, 18)
    if on then pxRect(5, y - 1, 390, 20, C.gold) end
    local n, l, c = shopRow(id)
    text(fitText(n, "small", 160), 12, y + 1, "small", id == "reset" and C.bad or C.cream)
    text(fitText(l, "tiny", 380 - 176 - fw("small", c) - 8), 176, y + 2, "tiny", C.dim)
    text(c, 12, y + 1, "small", C.gold, "right", 376)
  end
  keys(l3("skeys"))
end
local function drawShopBottom()
  col(hex("#f3ead3")); love.graphics.rectangle("fill", 0, 0, 320, 240)
  local id = SHOP_ROWS[S.ssel]
  local it = shopItem(id)
  local n = shopRow(id)
  text(n, 10, 6, "body", C.ink)
  local brown = hex("#6c5233")
  if it then
    text(it.d(), 10, 28, "small", brown, "left", 300)
    text(it.lvl(S), 10, 74, "small", C.ink)
    local ok = it.ok(S)
    local lbl = ok and (t("shop.buy") .. "  " .. P.eur(it.cost(S))) or t("shop.done")
    plateBtn(lbl, 10, 98, function() buyItem(it) end, 170, 26, ok and S.money < it.cost(S))
  elseif id == "team" then
    -- the team, a line a person: name and role, speed and the second skill (cooking or charm) as n/5, wage
    local y = 28
    for k, cx in ipairs({ 10, 128, 206 }) do text(l3("stcols")[k], cx, y, "tiny", brown) end; y = y + 17
    for _, p in ipairs(S.staff) do
      text(fitText(p.n .. " · " .. t("staff." .. p.r), "tiny", 128), 10, y + 1, "tiny", C.ink)
      text(p.sp .. " · " .. p.sk, 142, y + 1, "tiny", C.ink)
      text((P.eur(p.w):gsub("%.00$", "")), 206, y + 1, "tiny", brown)
      if #G.crew(S, p.r) > 1 then
        local who = p
        plateBtn(t("staff.fire"), 236, y, function() local x = G.letGo(S, who.id); if x then toast(t("ts.fired2", { x = x.n })); dirty = true end end, 78, 18)
      end
      y = y + 21
    end
  elseif id == "hire" then
    local day = S.candDay
    local cands = G.candidates(S)
    if day ~= S.candDay then dirty = true end   -- a new day brought new people
    text(t("staff.candlead", { c = P.eur(D.HIRE_COST) }), 10, 28, "tiny", brown, "left", 300)
    local y = 92
    if #cands == 0 then text(t("staff.none"), 10, y, "small", C.ink, "left", 300) end
    for k, cx in ipairs({ 10, 128, 206 }) do text(l3("stcols")[k], cx, y - 17, "tiny", brown) end
    for _, p in ipairs(cands) do
      text(fitText(p.n .. " · " .. t("staff." .. p.r), "tiny", 128), 10, y + 2, "tiny", C.ink)
      text(p.sp .. " · " .. p.sk, 142, y + 2, "tiny", C.ink)
      text((P.eur(p.w):gsub("%.00$", "")), 206, y + 2, "tiny", brown)
      local full, who = #G.crew(S, p.r) >= D.MAX_STAFF[p.r], p
      plateBtn(t(full and "staff.full" or "staff.hire"), 236, y, function()
        if full then return end
        local x = G.hire(S, who.id); if x then toast(t("ts.hired", { x = x.n })); dirty = true end
      end, 78, 20, not full and S.money < D.HIRE_COST)
      y = y + 23
    end
  elseif id == "bank" then
    local owe = S.loan or 0
    text(t("bank.lead", { r = (P.lang() == "pt" and "0,5" or "0.5") }), 10, 28, "tiny", brown, "left", 300)
    local rows = { { t("bank.owe"), P.eur(owe) }, { t("bank.today"), P.eur(owe * D.BANK_RATE) }, { t("bank.limit"), P.eur(D.BANK_MAX) } }
    for k, r in ipairs(rows) do
      text(r[1], 10, 92 + (k - 1) * 16, "small", C.ink); text(r[2], 10, 92 + (k - 1) * 16, "small", C.ink, "right", 300)
    end
    local x = 10
    for _, v in ipairs({ 500, 2000, 5000 }) do
      local amt = v
      x = plateBtn(t("bank.borrow", { x = P.eur(v):gsub("%.00$", "") }), x, 150, function()
        if G.borrow(S, amt) then toast(t("bank.got", { x = P.eur(amt):gsub("%.00$", "") })); dirty = true
        else toast(t("bank.max", { x = P.eur(D.BANK_MAX):gsub("%.00$", "") })) end
      end, 96, 24) + 6
    end
    local function pay(v) local x = G.repay(S, v); if x then toast(t("bank.paid", { x = P.eur(x) })); dirty = true end end
    plateBtn(t("bank.repay", { x = "$500" }), 10, 182, function() pay(500) end, 146, 24, owe > 0 and S.money < math.min(500, owe))
    plateBtn(t("bank.all"), 164, 182, function() pay(nil) end, 146, 24, owe > 0 and S.money < owe)
  elseif id == "supplier" then
    text(t("sup.lead"), 10, 28, "tiny", brown, "left", 300)
    for k = 1, 3 do
      local y = 92 + (k - 1) * 48
      local sp = D.SUPPLIER[k]
      plateBtn(fitText(t("sup." .. k), "tiny", 126), 10, y, function() setSupplier(k) end, 130, 34, S.supplier == k)
      text(k == 1 and t("sup.d1") or t("sup.d", { q = sp.q, m = math.floor((sp.m - 1) * 100 + .5) }), 148, y + 2, "tiny", brown, "left", 162)
    end
  elseif id == "study" then
    text(t("study.lead"), 10, 28, "tiny", brown, "left", 300)
    local done = S.studyWeek == G.weekOf(S.day)
    plateBtn(fitText(done and t("study.done") or (t("study.btn") .. "  " .. P.eur(D.STUDY_COST)), "tiny", 290), 10, 92, runStudy, 300, 24)
    local y = 124
    for _, x in ipairs(S.tips) do
      for _, line in ipairs(G.tipText(x)) do
        if y > 210 then break end
        text("- " .. line, 10, y, "tiny", C.ink, "left", 300)
        local _, wr = fonts.tiny.f:getWrap("- " .. line, 300 / fonts.tiny.s)
        y = y + #wr * fonts.tiny.f:getHeight() * fonts.tiny.s + 2
      end
    end
  elseif id == "room" then
    local A = G.roomStats(S)
    text(t("rm.seats", { n = A.seats }) .. (A.nblocked > 0 and ("  ·  X " .. A.nblocked) or ""), 10, 30, "small", brown)
    plateBtn(l3("edroom"), 10, 56, openEditor, 300, 26)
  else
    plateBtn(isArmed("reset") and t("ts.sure") or t("shop.reset"), 10, 40, resetGame, 300, 26, true)
  end
end

-- ---------------------------------------------------------------- the city
--[[ Porto Magno (city.js): the streets and houses on top (gfx/city.png, painted by tools/export_3ds_city.js, 904x704),
     and on the touch screen a navigator (the whole town small, gfx/city_mini.png) next to the chosen building. Touch
     or drag on the navigator to look somewhere, or use the D-pad to jump to the next building worth seeing in that
     direction (to rent, for sale, a rival, your shops, the landmarks); A rents, buys or goes to your shop (press
     twice), Y closes or sells it, X zooms in. ]]
local CL = D.CITY.LOTS
local cityImg, cityMini
local city = { sel = nil, z = 1, armed = nil, cam = nil, drag = false }
local CITY_MINI_W, MINI_X, MINI_Y = 152, 4, 4   -- the navigator (as made by tools/export_3ds_city.js)
local CITY_MINI_H = math.floor(CITY_MINI_W * D.CITY.LH / D.CITY.LW + .5)
local MINI_K = CITY_MINI_W / D.CITY.LW
local CITY_TOP = 20   -- below the header
local function cityShown(i) local k = G.lotKind(S, i); return k == "rent" or k == "sale" or k == "rival" or k == "mine" or k == "land" end
local function cityPick(dx, dy)   -- the nearest building worth seeing in that direction
  local a = CL[city.sel]
  local ax, ay = a.x + a.w / 2, a.y + a.h / 2
  local best, bs
  for i, l in ipairs(CL) do
    if i ~= city.sel and cityShown(i) then
      local x, y = l.x + l.w / 2 - ax, l.y + l.h / 2 - ay
      local along, across = x * dx + y * dy, math.abs(x * dy - y * dx)
      if along > 4 then
        local sc = along + across * 2
        if not bs or sc < bs then best, bs = i, sc end
      end
    end
  end
  if best then city.sel, city.armed = best, nil end
end
local function cityPickAt(mx, my)   -- the building worth seeing nearest to a point of the map
  local best, bd
  for i, l in ipairs(CL) do
    if cityShown(i) then
      local d = (l.x + l.w / 2 - mx) ^ 2 + (l.y + l.h / 2 - my) ^ 2
      if not bd or d < bd then best, bd = i, d end
    end
  end
  if best and best ~= city.sel then city.sel, city.armed = best, nil end
end
local function inMini(x, y) return x >= MINI_X and x < MINI_X + CITY_MINI_W and y >= MINI_Y and y < MINI_Y + CITY_MINI_H end
local function cityTouch(x, y) cityPickAt((x - MINI_X) / MINI_K, (y - MINI_Y) / MINI_K) end
local function cityAct(close)   -- A: rent / buy / go to the shop; Y: close or sell your shop (each pressed twice)
  local i = city.sel
  local k = G.lotKind(S, i)
  if close then
    if k ~= "mine" or #S.shops < 2 then return end
    if city.armed ~= "c" .. i then city.armed = "c" .. i; toast(t("city.sure")); return end
    city.armed = nil
    local name, gain = G.closeShop(S, G.lotShop(S, i))
    if name then toast(gain > 0 and t("city.sold", { x = name, p = P.eur(gain):gsub("%.00$", "") }) or t("city.closed", { x = name })); syncWorld(); dirty = true end
    return
  end
  if k == "mine" then
    local own = G.lotShop(S, i)
    if own ~= S.cur and G.openShop(S, own) then clampSel(); syncWorld(); dirty = true; toast(t("shop.now", { x = G.shopName(S) })) end
  elseif k == "rent" or k == "sale" then
    if G.ownMoney(S) < D.CITY_CASH then toast(t("city.need", { m = P.eur(D.CITY_CASH):gsub("%.00$", "") })); return end
    if city.armed ~= i then city.armed = i; toast(t("city.sure")); return end
    city.armed = nil
    local ok, why = G.openLot(S, i, k == "sale")
    if ok then clampSel(); syncWorld(); dirty = true; toast(t("city.open.t", { x = G.shopName(S) }))
    elseif why then toast(t(why, { m = P.eur(D.CITY_CASH):gsub("%.00$", "") })) end
  end
end
local function drawCityTop()
  col(C.bg); love.graphics.rectangle("fill", 0, 0, 400, 240)
  if not cityImg then cityImg = love.graphics.newImage("gfx/city.png") end
  city.sel = city.sel or S.shops[S.cur].lot
  local z, l = city.z, CL[city.sel]
  local vw, vh = 400 / z, (240 - CITY_TOP - 18) / z
  local cx = math.max(0, math.min(D.CITY.LW - vw, l.x + l.w / 2 - vw / 2))
  local cy = math.max(0, math.min(D.CITY.LH - vh, l.y + l.h / 2 - vh / 2))
  if vw > D.CITY.LW then cx = (D.CITY.LW - vw) / 2 end
  city.cam = { x = cx, y = cy, w = vw, h = vh }   -- shown as a frame on the navigator
  local function P2(x, y) return math.floor((x - cx) * z), math.floor((y - cy) * z) + CITY_TOP end
  love.graphics.setScissor(0, CITY_TOP, 400, 240 - CITY_TOP - 18)
  local ix, iy = P2(0, 0)
  col({ 1, 1, 1 }); love.graphics.draw(cityImg, ix, iy, 0, z, z)
  -- signs and pins: to rent / for sale, rivals, your shops (* the one open), the landmarks
  for i, x in ipairs(CL) do
    local k = G.lotKind(S, i)
    local px, py = P2(x.x + x.w / 2, x.y + x.h / 2)
    if k == "rent" or k == "sale" or k == "rival" or k == "mine" or k == "land" then
      local s2 = k == "land" and P.upper(t("land." .. x.land)) or k == "rent" and P.upper(l3("rent")) or k == "sale" and P.upper(l3("sale"))
        or k == "rival" and t("city.pin.rival") or (t("city.pin.mine") .. (G.lotShop(S, i) == S.cur and " *" or ""))
      local c = hex(D.CITY.KCOL[k] or "#2a1407")
      do
        local w = fw("tiny", s2) + 8
        col(hex("#120a04")); love.graphics.rectangle("fill", px - w / 2 - 1, py - 9, w + 2, 18)
        col(k == "land" and hex("#2a1407", .85) or c); love.graphics.rectangle("fill", px - w / 2, py - 8, w, 16)
        text(s2, px - w / 2, py - 7, "tiny", k == "land" and C.combo or hex("#ffffff"), "center", w)
      end
    end
  end
  local x0, y0 = P2(l.x, l.y)
  col(hex("#120a04")); love.graphics.setLineWidth(3); love.graphics.rectangle("line", x0, y0, l.w * z, l.h * z)
  col(C.combo); love.graphics.setLineWidth(1); love.graphics.rectangle("line", x0 + .5, y0 + .5, l.w * z - 1, l.h * z - 1)
  love.graphics.setScissor()
  drawHeader()
  keys(l3("citykeys"))
end
local function drawCityBottom()
  col(hex("#f3ead3")); love.graphics.rectangle("fill", 0, 0, 320, 240)
  if not cityMini then cityMini = love.graphics.newImage("gfx/city_mini.png") end
  city.sel = city.sel or S.shops[S.cur].lot
  local i = city.sel
  local l, k = CL[i], G.lotKind(S, i)
  local own = G.lotShop(S, i)
  local brown = hex("#6c5233")
  -- the navigator: the whole town, a dot on each building worth seeing, the top screen's view as a frame
  col(hex("#120a04")); love.graphics.rectangle("fill", MINI_X - 2, MINI_Y - 2, CITY_MINI_W + 4, CITY_MINI_H + 4)
  col({ 1, 1, 1 }); love.graphics.draw(cityMini, MINI_X, MINI_Y)
  for j, x in ipairs(CL) do
    local kk = G.lotKind(S, j)
    if kk == "rent" or kk == "sale" or kk == "rival" or kk == "mine" then
      local px, py = MINI_X + (x.x + x.w / 2) * MINI_K, MINI_Y + (x.y + x.h / 2) * MINI_K
      col(hex("#120a04")); love.graphics.rectangle("fill", math.floor(px) - 2, math.floor(py) - 2, 5, 5)
      col(hex(D.CITY.KCOL[kk])); love.graphics.rectangle("fill", math.floor(px) - 1, math.floor(py) - 1, 3, 3)
    end
  end
  if city.cam then
    local c = city.cam
    local fx, fy = math.floor(MINI_X + c.x * MINI_K), math.floor(MINI_Y + c.y * MINI_K)   -- the camera stays inside the map
    local fw2, fh2 = math.floor(c.w * MINI_K), math.floor(c.h * MINI_K)
    col(hex("#120a04")); love.graphics.rectangle("line", fx - .5, fy - .5, fw2 + 1, fh2 + 1)
    col(C.combo); love.graphics.rectangle("line", fx + .5, fy + .5, fw2 - 1, fh2 - 1)
  end
  -- the building
  local RX, RW = 164, 150
  local title = k == "land" and t("land." .. l.land) or k == "rival" and l.name or k == "mine" and G.shopName(S, own)
    or k == "taken" and t("biz." .. l.biz) or l.addr
  local chip = (k == "rent" or k == "sale") and l3(k) or t("city.k." .. k)   -- short words: the signs and chips are small
  local cw = fw("tiny", chip) + 8
  col(hex(D.CITY.KCOL[k] or "#7a6a55")); love.graphics.rectangle("fill", RX, 3, cw, 16)
  text(chip, RX, 4, "tiny", hex("#ffffff"), "center", cw)
  text(fitText(t("hood." .. l.hood), "tiny", RW - cw - 6), RX + cw + 6, 4, "tiny", brown)
  local F = fonts.tiny
  local function wrapped(str, y, c)   -- a paragraph in the right column; returns the next y
    local _, lines = F.f:getWrap(str, RW / F.s)
    text(str, RX, y, "tiny", c or brown, "left", RW)
    return y + #lines * F.f:getHeight() * F.s + 2
  end
  local y = wrapped(title, 22, C.ink) + 2
  local function row(a2, b2) text(a2, RX, y, "tiny", C.ink); text(b2, RX, y, "tiny", C.ink, "right", RW); y = y + 15 end
  if k == "land" then
    y = wrapped(t("land.d." .. l.land), y)
    if l.land == "square" then y = wrapped(t("city.contest"), y + 2) end
  else
    if title ~= l.addr then y = wrapped(l.addr, y) end
    if k == "rival" then
      y = wrapped(t("rv.style") .. ": " .. t("rv." .. (l.name == "Pizza Rápida" and "classic" or D.HOOD_STYLE[l.hood])), y)
    else
      row(t("city.traffic"), l.traffic .. "/5")
      if k == "rent" or k == "sale" then
        row(t("city.cond"), t("city.c." .. l.cond) .. (l.cond == "works" and (" · " .. P.eur(l.works):gsub("%.00$", "")) or ""))
      end
      if k == "sale" then row(t("city.price"), (P.eur(l.price):gsub("%.00$", "")))
      elseif k ~= "taken" then row(t("city.rent"), P.eur(own and G.rentOf(S, own) or l.rent):gsub("%.00$", "") .. t("city.perday")) end
    end
  end
  -- who comes in this neighbourhood, under the navigator
  y = MINI_Y + CITY_MINI_H + 6
  text(t("city.mix"), 10, y, "tiny", C.ink)
  text(t("city.yours") .. ": " .. #S.shops, 10, y, "tiny", brown, "right", 300); y = y + 16
  local mix, bx = D.CITY.HOODS[l.hood].mix, 10
  for j, g in ipairs(D.SEG_ORDER) do
    local w = math.floor(mix[j] / 100 * 300 + .5)
    col(hex(D.SEG[g].col)); love.graphics.rectangle("fill", bx, y, w, 8); bx = bx + w
  end
  y = y + 11
  for j, g in ipairs(D.SEG_ORDER) do   -- two by two
    text(t("seg." .. g) .. " " .. mix[j] .. "%", 10 + ((j - 1) % 2) * 150, y + math.floor((j - 1) / 2) * 14, "tiny", hex(D.SEG[g].col))
  end
  y = y + 32
  -- what you can do here
  if k == "rent" or k == "sale" then
    local buy = k == "sale"
    local can = G.ownMoney(S) >= D.CITY_CASH
    local lbl = city.armed == i and t("city.sure") or buy and (t("city.bBuy") .. " · " .. P.eur(G.lotCost(l, true)):gsub("%.00$", ""))
      or (t("city.bRent") .. " · " .. P.eur(l.rent):gsub("%.00$", "") .. t("city.perday"))
    plateBtn(fitText(lbl, "tiny", 290), 10, y, function() cityAct(false) end, 300, 22, not can)
    y = y + 25
    local w = l.cond == "works" and P.eur(l.works):gsub("%.00$", "") or "$0"
    text(fitText(can and (buy and t("city.cost.buy", { p = P.eur(l.price):gsub("%.00$", ""), w = w }) or t("city.cost.rent", { w = w, r = P.eur(l.rent):gsub("%.00$", "") }))
      or t("city.need", { m = P.eur(D.CITY_CASH):gsub("%.00$", "") }), "tiny", 300), 10, y, "tiny", brown)
  elseif k == "mine" then
    if own == S.cur then text(t("city.here"), 10, y + 4, "small", hex("#8a5a00"))
    else plateBtn(t("city.go"), 10, y, function() cityAct(false) end, 145, 22) end
    if #S.shops > 1 then
      local sh = S.shops[own]
      local lbl = city.armed == "c" .. i and t("city.sure") or sh.owned and t("city.sell", { x = P.eur(math.floor(l.price * D.SELL_SHARE + .5)):gsub("%.00$", "") }) or t("city.close")
      plateBtn(fitText(lbl, "tiny", 135), 165, y, function() cityAct(true) end, 145, 22, true)
    end
  end
end


local EDF = {}   -- the editor's functions (one local: main.lua is near Lua's 200 locals)
-- ---------------------------------------------------------------- the room editor (Shop › Decorate the room)
--[[ As the browser's (= UI: ROOM EDITOR =): the catalogue on the top screen (tabs with L/R, the list with up/down,
     A takes a piece, or buys a floor, a wall finish or the Christmas lights), the room on the touch screen: with a piece
     taken, touch where it goes (wall pieces on the back wall, in one of its slots); with none, touch a piece to select
     it, then X sells it for half its price and Y moves it. Tables with no way in are crossed out. ]]
EDF.TABS = { "table", "decor", "wall", "floor", "walls" }
function EDF.edEntries(tab)
  local out = {}
  if tab == "floor" or tab == "walls" then
    local src = tab == "floor" and RL.FLOORS or RL.WALLS
    for k, d in pairs(src) do out[#out + 1] = { kind = tab, id = k, d = d, name = t((tab == "floor" and "rm.f." or "rm.w.") .. k) } end
  else
    for k, d in pairs(RL.ITEMS) do if d.cat == tab then out[#out + 1] = { kind = "item", id = k, d = d, name = t("rm.i." .. k) .. (d.n and (" · " .. d.n) or "") } end end
  end
  table.sort(out, function(a, b) return a.d.price < b.d.price or (a.d.price == b.d.price and a.id < b.id) end)
  return out
end
openEditor = function() ED = { tab = 1, sel = 1 }; idleScene = nil; SALA.OY = 0 end
function EDF.edChanged() local room = G.room(S); room.rev = (room.rev or 0) + 1; idleScene = nil; dirty = true end
function EDF.edPay(v) if S.money < v then toast(t("rm.nomoney")); return false end; S.money = r2(S.money - v); return true end
function EDF.edRefund(v) S.money = r2(S.money + math.floor(v * .5 + .5)) end
function EDF.edActivate()
  local e = EDF.edEntries(EDF.TABS[ED.tab])[ED.sel]; if not e then return end
  local room = G.room(S)
  if e.kind == "floor" then if room.floor ~= e.id and EDF.edPay(e.d.price) then room.floor = e.id; EDF.edChanged() end; return end
  if e.kind == "walls" then if room.wall ~= e.id and EDF.edPay(e.d.price) then room.wall = e.id; EDF.edChanged() end; return end
  if e.d.strip then   -- the Christmas lights: the whole back wall, bought or sold with one press
    if room.lights then room.lights = false; EDF.edRefund(e.d.price); EDF.edChanged() elseif EDF.edPay(e.d.price) then room.lights = true; EDF.edChanged() end
    return
  end
  ED.tool, ED.moving, ED.pick = e.id, nil, nil
end
function EDF.edSell()
  local room, pk = G.room(S), ED.pick; if not pk then return end
  if pk.wall then local id = room.walls[pk.wall]; if id then room.walls[pk.wall] = false; EDF.edRefund(RL.ITEMS[id].price) end
  else for i, it in ipairs(room.items) do if it == pk then table.remove(room.items, i); EDF.edRefund(RL.ITEMS[it.id].price); break end end end
  ED.pick = nil; EDF.edChanged()
end
--[[ Touch: a piece of the room is dragged where it goes and lands when the stylus lifts (the ghost's frame is green
     where it fits, red where not); a piece taken from the catalogue is placed the same way. Wall pieces go in a slot
     of the back wall with a tap. ]]
function EDF.edPoint(x, y) return x * 2, (y + SALA.OY) * 2 end   -- the touch screen shows the room at half size
function EDF.edTile(id, X, Y, dc, dr)
  local d = RL.ITEMS[id]
  if dc then return math.floor(X / 32) - dc, math.floor(Y / 32) - dr end
  return math.floor(X / 32 - d.w / 2 + .5), math.floor(Y / 32 - d.h / 2 + .5)
end
function EDF.edPlace(c, r)   -- puts the taken (or moving) piece at c, r if it fits; true when it did
  local room, d = G.room(S), RL.ITEMS[ED.tool]
  if not RL.fits(room, ED.tool, c, r, ED.moving) then toast(l3("ednofit")); return false end
  local was = G.roomStats(S).nblocked
  if ED.moving then ED.moving.c, ED.moving.r = c, r; ED.pick = ED.moving
  elseif EDF.edPay(d.price) then local it = { id = ED.tool, c = c, r = r }; room.items[#room.items + 1] = it; ED.pick = it
  else return false end
  EDF.edChanged()
  local A = G.roomStats(S)
  if ED.pick and A.blocked[ED.pick] then toast(t("rm.t.noseat"):gsub("%s*%(.-%)", "")) elseif A.nblocked > was then toast(t("rm.w.blocked", { n = A.nblocked }):gsub("%s*%(.-%)", "")) end
  return true
end
function EDF.edTouch(x, y)
  local room, X, Y = G.room(S), EDF.edPoint(x, y)
  local T = 32
  if ED.tool and RL.ITEMS[ED.tool].cat == "wall" then
    local d = RL.ITEMS[ED.tool]
    if Y < 2 * T and X < 12 * T then
      local slot = math.floor(X / 64) + 1
      if room.walls[slot] ~= ED.tool and EDF.edPay(d.price) then
        if room.walls[slot] then EDF.edRefund(RL.ITEMS[room.walls[slot]].price) end
        room.walls[slot] = ED.tool; ED.tool = nil; ED.pick = { wall = slot }; EDF.edChanged()
      end
    else toast(l3("ednofit")) end
    return
  end
  if ED.tool then   -- a piece from the catalogue (or one being moved with Y): it follows the stylus until it lifts
    local c, r = EDF.edTile(ED.tool, X, Y)
    ED.ghost, ED.drag = { c = c, r = r }, { new = true }
    return
  end
  if Y < 2 * T and X < 12 * T then local slot = math.floor(X / 64) + 1; ED.pick = room.walls[slot] and { wall = slot } or nil; return end
  local it = RL.hit(room, X, Y)
  ED.pick = it
  if it then   -- held: it moves with the stylus
    ED.drag = { it = it, dc = math.floor(X / T) - it.c, dr = math.floor(Y / T) - it.r, c0 = it.c, r0 = it.r }
    ED.ghost = { c = it.c, r = it.r }
  end
end
function EDF.edMove(x, y)
  local dg = ED.drag; if not dg then return end
  local X, Y = EDF.edPoint(x, y)
  if dg.new then local c, r = EDF.edTile(ED.tool, X, Y); ED.ghost = { c = c, r = r }; return end
  local c, r = EDF.edTile(dg.it.id, X, Y, dg.dc, dg.dr)
  if c ~= ED.ghost.c or r ~= ED.ghost.r then
    ED.ghost = { c = c, r = r }
    dg.moved = true
    dg.it.c, dg.it.r = c, r; idleScene = nil   -- drawn where the stylus is
  end
end
function EDF.edUp()
  local dg = ED.drag; if not dg then return end
  ED.drag = nil
  if dg.new then
    if EDF.edPlace(ED.ghost.c, ED.ghost.r) then ED.tool, ED.moving = nil, nil end
    ED.ghost = nil
    return
  end
  local it = dg.it
  local c, r = it.c, it.r
  it.c, it.r = dg.c0, dg.r0; idleScene = nil
  ED.ghost = nil
  if not dg.moved or (c == dg.c0 and r == dg.r0) then return end
  ED.tool, ED.moving = it.id, it
  EDF.edPlace(c, r)
  ED.tool, ED.moving = nil, nil
end
function EDF.edButton(b)
  local n = #EDF.edEntries(EDF.TABS[ED.tab])
  if b == "leftshoulder" or b == "rightshoulder" then ED.tab = (ED.tab - 1 + (b == "leftshoulder" and -1 or 1)) % #EDF.TABS + 1; ED.sel = 1
  elseif b == "dpup" then ED.sel = math.max(1, ED.sel - 1)
  elseif b == "dpdown" then ED.sel = math.min(n, ED.sel + 1)
  elseif b == "a" then EDF.edActivate()
  elseif b == "x" then EDF.edSell()
  elseif b == "y" then if ED.pick and not ED.pick.wall then ED.tool, ED.moving = ED.pick.id, ED.pick end
  elseif b == "b" then if ED.tool or ED.pick then ED.tool, ED.moving, ED.pick, ED.ghost = nil, nil, nil, nil else ED = nil; idleScene = nil; SALA.OY = 16 end end
end
function EDF.drawEditorTop()
  col(C.bg); love.graphics.rectangle("fill", 0, 0, 400, 240)
  drawHeader()
  local x = 6
  for i, k in ipairs(EDF.TABS) do   -- the tabs
    local s = t("rm.tab." .. k)
    text(s, x, 23, "tiny", i == ED.tab and C.gold or C.dim)
    if i == ED.tab then col(C.gold); love.graphics.rectangle("fill", x, 38, fw("tiny", s), 1) end
    x = x + fw("tiny", s) + 10
  end
  local list, room = EDF.edEntries(EDF.TABS[ED.tab]), G.room(S)
  local top = math.max(0, math.min(ED.sel - 4, #list - 8))
  for i = top + 1, math.min(#list, top + 8) do   -- the list: name, style, price
    local e, y = list[i], 43 + (i - top - 1) * 19
    local mine = (e.kind == "floor" and room.floor == e.id) or (e.kind == "walls" and room.wall == e.id) or (e.d.strip and room.lights) or ED.tool == e.id
    col(i == ED.sel and hex("#4a260f") or C.panel); love.graphics.rectangle("fill", 4, y, 252, 17)
    if i == ED.sel then pxRect(3, y - 1, 254, 19, C.gold) end
    text(fitText((mine and "> " or "") .. e.name, "tiny", 140), 8, y + 1, "tiny", mine and C.gold or C.cream)
    text(fitText(t("rm.st." .. e.d.style), "tiny", 60), 150, y + 1, "tiny", C.dim)
    text((P.eur(e.d.price):gsub("%.00$", "")), 8, y + 1, "tiny", S.money < e.d.price and C.bad or C.gold, "right", 244)
  end
  local A = G.roomStats(S)   -- on the right: seats and the atmosphere for each group
  text(t("rm.seats", { n = A.seats }), 266, 44, "small", C.cream)
  if A.nblocked > 0 then text("X " .. A.nblocked, 266, 62, "small", C.bad) end
  text(fitText(t("rm.atm"), "tiny", 130), 266, 82, "tiny", C.dim)
  for i, k in ipairs(D.SEG_ORDER) do
    local y = 100 + (i - 1) * 24
    text(fitText(t("seg." .. k), "tiny", 128), 266, y, "tiny", C.cream)
    col(hex("#120a04")); love.graphics.rectangle("fill", 266, y + 15, 124, 5)
    col(hex(D.SEG[k].col)); love.graphics.rectangle("fill", 266, y + 15, 124 * A.atm[k] / 100, 5)
  end
  local line
  if ED.tool then line = l3("edplace")
  elseif ED.pick then
    local id = ED.pick.wall and room.walls[ED.pick.wall] or ED.pick.id
    line = t("rm.i." .. id) .. ":  " .. l3("edpick"):gsub("{x}", P.eur(math.floor(RL.ITEMS[id].price * .5 + .5)))
  else line = l3("edhint") end
  text(fitText(line, "tiny", 390), 0, 207, "tiny", C.combo, "center", 400)
  keys(l3("edkeys"))
end
function EDF.drawEditorBottom()
  if not idleScene then idleScene = SALA.scene(S, G) end
  SALA.draw(nil, idleScene, S)
  local room, A, OY = G.room(S), G.roomStats(S), SALA.OY
  local function box(c, r, w, h, colr) col(colr); love.graphics.rectangle("line", c * 16 + .5, r * 16 - OY + .5, w * 16 - 1, h * 16 - 1) end
  for _, it in ipairs(room.items) do   -- tables with no way in: crossed out in red
    if A.blocked[it] then
      local d = RL.ITEMS[it.id]; local x0, y0 = it.c * 16, it.r * 16 - OY
      col(C.bad); love.graphics.setLineWidth(2)
      love.graphics.line(x0 + 4, y0 + 4, x0 + d.w * 16 - 4, y0 + d.h * 16 - 4); love.graphics.line(x0 + d.w * 16 - 4, y0 + 4, x0 + 4, y0 + d.h * 16 - 4)
      love.graphics.setLineWidth(1)
    end
  end
  if ED.tool and RL.ITEMS[ED.tool].cat == "wall" then for i = 0, 5 do box(i * 2, 0, 2, 2, hex("#ffd34a", .8)) end end
  local gid = ED.tool or (ED.drag and ED.drag.it and ED.drag.it.id)
  if ED.ghost and gid then
    local d = RL.ITEMS[gid]
    box(ED.ghost.c, ED.ghost.r, d.w, d.h, RL.fits(room, gid, ED.ghost.c, ED.ghost.r, ED.moving or (ED.drag and ED.drag.it)) and C.good or C.bad)
  end
  if ED.pick and not ED.drag then
    if ED.pick.wall then box((ED.pick.wall - 1) * 2, 0, 2, 2, C.gold)
    else local d = RL.ITEMS[ED.pick.id]; box(ED.pick.c, ED.pick.r, d.w, d.h, C.gold) end
  end
end
-- ---------------------------------------------------------------- Options (START): language, music, quit
local OPT = { rows = { "lang", "music", "vol", "next", "quit" } }
function OPT.value(id)
  if id == "lang" then return P.lang() == "pt" and "Português" or "English" end
  if id == "music" then return l3(MUS.on and "on" or "off") end
  if id == "vol" then return t("mus.v" .. MUS.vol) end
  if id == "next" then return MUS.on and MUS.title() or "" end
  return ""
end
function OPT.name(id)
  return id == "lang" and t("lang.title") or id == "music" and t("mus.title") or id == "vol" and t("mus.vol")
    or id == "next" and t("mus.next") or l3("quit")
end
function OPT.act(id, step)
  if id == "lang" then setLang(P.lang() == "pt" and "en" or "pt"); dirty = true
  elseif id == "music" then MUS.setOn(not MUS.on); dirty = true
  elseif id == "vol" then MUS.setVol(math.max(1, math.min(5, MUS.vol + (step or 1)))); dirty = true
  elseif id == "next" then MUS.on = true; MUS.play(); dirty = true
  elseif id == "quit" then save(); love.event.quit() end
end
function OPT.button(b)
  if b == "dpup" then OPT.sel = math.max(1, OPT.sel - 1)
  elseif b == "dpdown" then OPT.sel = math.min(#OPT.rows, OPT.sel + 1)
  elseif b == "dpleft" or b == "dpright" then local id = OPT.rows[OPT.sel]; if id ~= "quit" and id ~= "next" then OPT.act(id, b == "dpleft" and -1 or 1) end
  elseif b == "a" then OPT.act(OPT.rows[OPT.sel])
  elseif b == "b" or b == "start" then OPT.open = false end
end
function OPT.drawTop()
  col(C.bg); love.graphics.rectangle("fill", 0, 0, 400, 240)
  col(C.panel); love.graphics.rectangle("fill", 0, 0, 400, 20)
  text(t("opt.title"), 8, 2, "body", C.gold)
  text("Pizza Magna " .. (D.VERSION or "?"), 6, 4, "tiny", C.dim, "right", 388)   -- the build, for bug reports
  for k, id in ipairs(OPT.rows) do
    local y = 30 + (k - 1) * 30
    local on = k == OPT.sel
    col(on and hex("#4a260f") or C.panel); love.graphics.rectangle("fill", 20, y, 360, 24)
    if on then pxRect(19, y - 1, 362, 26, C.gold) end
    text(OPT.name(id), 30, y + 4, "body", id == "quit" and C.bad or C.cream)
    local v = OPT.value(id)
    if v ~= "" then text(fitText((on and id ~= "next" and "‹ " .. v .. " ›" or v), "small", 190), 30, y + 6, "small", C.gold, "right", 340) end
  end
  text(l3("okeys"), 0, 223, "tiny", C.dim, "center", 400)
end
function OPT.drawBottom()
  col(hex("#f3ead3")); love.graphics.rectangle("fill", 0, 0, 320, 240)
  for k, id in ipairs(OPT.rows) do
    local kk = k
    plateBtn(OPT.name(id) .. (OPT.value(id) ~= "" and id ~= "next" and ":  " .. OPT.value(id) or ""), 20, 14 + (k - 1) * 36, function() OPT.sel = kk; OPT.act(id) end, 280, 28, id == "quit")
  end
  plateBtn(l3("back"), 110, 200, function() OPT.open = false end, 100, 26)
end

drawBottom = function()
  hits = {}
  if OPT.open then OPT.drawBottom()
  elseif ED then EDF.drawEditorBottom()
  elseif report then drawReportBottom()
  elseif S.tab == "menu" then drawMenuBottom()
  elseif S.tab == "day" then drawDayBottom()
  elseif S.tab == "contest" then drawContestBottom()
  elseif S.tab == "shop" then drawShopBottom()
  elseif S.tab == "city" then drawCityBottom()
  else drawKitchenBottom() end
end
drawTopScreen = function()
  if OPT.open then OPT.drawTop()
  elseif ED then EDF.drawEditorTop()
  elseif report then drawReportTop()
  elseif S.tab == "menu" then drawMenuTop()
  elseif S.tab == "day" and histOn and not anim then drawHistTop()
  elseif S.tab == "day" then drawDayTop()
  elseif S.tab == "contest" then drawContestTop()
  elseif S.tab == "shop" then drawShopTop()
  elseif S.tab == "city" then drawCityTop()
  else drawTop() end
  drawToast()
end

-- ---------------------------------------------------------------- input
local drag = nil
local function benchPoint(x, y) return (x - PCX) / PR, (y - PCY) / PR end
local function touchDown(x, y)
  if renaming and not CONSOLE then finishRename(renameBuf) end   -- PC: a tap elsewhere keeps what was typed
  if OPT.open then for k = #hits, 1, -1 do local h = hits[k]; if x >= h.x and x < h.x + h.w and y >= h.y and y < h.y + h.h then h.fn(); return end end; return end
  if S.tab == "city" and not report and inMini(x, y) then city.drag = true; cityTouch(x, y); return end
  if ED and S.tab == "shop" then EDF.edTouch(x, y); return end
  for k = #hits, 1, -1 do
    local h = hits[k]
    if x >= h.x and x < h.x + h.w and y >= h.y and y < h.y + h.h then h.fn(); return end
  end
  if S.tab ~= "kitchen" then return end
  if KP.touch(x, y) then return end
  local px, py = benchPoint(x, y)
  if math.sqrt(px * px + py * py) > 1 then return end
  drag = { x = 9, y = 9 }
  if addPiece(px, py) then drag = { x = px, y = py } end
end
local function touchMove(x, y)
  if ED and S.tab == "shop" then EDF.edMove(x, y); return end
  if city.drag then if inMini(x, y) then cityTouch(x, y) end; return end
  if not drag then return end
  local px, py = benchPoint(x, y)
  if math.sqrt((px - drag.x) ^ 2 + (py - drag.y) ^ 2) > .2 and addPiece(px, py) then drag = { x = px, y = py } end
end
local function touchUp() drag = nil; city.drag = false; if ED and S.tab == "shop" then EDF.edUp() end end

local held = {}
local function navButton(b)   -- outside the Kitchen: L/R and SELECT go through the screens, START quits
  if b == "leftshoulder" then goTab(-1)
  elseif b == "rightshoulder" or b == "back" then goTab(1) end
end
local function otherButton(b)
  if report then if b == "a" then closeReport() end; return end
  if S.tab == "day" then
    if anim then
      if b == "a" then skipDay()
      elseif b == "b" then anim.paused = not anim.paused   -- the clock stops; the room is still drawn
      elseif b == "dpleft" then anim.speed = math.max(1, anim.speed / 2); anim.paused = false
      elseif b == "dpright" then anim.speed = math.min(4, anim.speed * 2); anim.paused = false end
    elseif b == "a" then startDay()
    elseif b == "y" then histOn = not histOn
    else navButton(b) end
  elseif S.tab == "contest" then
    if b == "dpup" then S.csel = math.max(1, S.csel - 1)
    elseif b == "dpdown" then S.csel = math.min(#S.menu, S.csel + 1)
    elseif b == "a" and S.menu[S.csel] then enterContest(S.menu[S.csel])
    else navButton(b) end
  elseif S.tab == "city" then
    city.sel = city.sel or S.shops[S.cur].lot
    if b == "dpleft" then cityPick(-1, 0) elseif b == "dpright" then cityPick(1, 0)
    elseif b == "dpup" then cityPick(0, -1) elseif b == "dpdown" then cityPick(0, 1)
    elseif b == "a" then cityAct(false)
    elseif b == "y" then cityAct(true)
    elseif b == "x" then city.z = city.z == 1 and 2 or 1
    else navButton(b) end
  elseif S.tab == "shop" then
    if b == "dpup" then S.ssel = math.max(1, S.ssel - 1); armed = nil
    elseif b == "dpdown" then S.ssel = math.min(#SHOP_ROWS, S.ssel + 1); armed = nil
    elseif b == "a" then shopAction(SHOP_ROWS[S.ssel])
    else navButton(b) end
  end
end
local function menuButton(b)
  if b == "dpup" then pickRow(-1)
  elseif b == "dpdown" then pickRow(1)
  elseif b == "dpleft" then priceStep(-.5)
  elseif b == "dpright" then priceStep(.5)
  elseif b == "a" then editPizza()
  elseif b == "x" then renamePizza()
  elseif b == "y" then removePizza()
  else navButton(b) end
end
local function button(b)
  if OPT.open then OPT.button(b); return end
  if b == "start" then OPT.open, OPT.sel = true, 1; return end
  if ED and S.tab == "shop" then EDF.edButton(b); return end
  if report or S.tab == "day" or S.tab == "contest" or S.tab == "shop" or S.tab == "city" then otherButton(b); return end
  if S.tab == "menu" then menuButton(b); return end
  if b == "dpleft" or b == "dpright" or b == "dpup" or b == "dpdown" then KP.button(b)
  elseif b == "leftshoulder" then goTab(-1)
  elseif b == "rightshoulder" then goTab(1)
  elseif b == "a" then setCut(1 - curCut())
  elseif b == "x" then rotatePiece()
  elseif b == "b" then undo()
  elseif b == "y" then clear()
  elseif b == "back" then goTab(1) end
end
local REPEAT = { dpleft = true, dpright = true, dpup = true, dpdown = true }
local function press(b) button(b); if REPEAT[b] then held[b] = .35 end end
local function release(b) held[b] = nil end

function love.gamepadpressed(_, b) press(b) end
function love.gamepadreleased(_, b) release(b) end
-- PC keys: arrows, Q/W shoulders, Z=A, X=B, A=Y, S=X, Tab=SELECT, Esc=START
local KEYS = { left = "dpleft", right = "dpright", up = "dpup", down = "dpdown", q = "leftshoulder", w = "rightshoulder",
  z = "a", x = "b", s = "x", a = "y", tab = "back", escape = "start" }
function love.keypressed(k)
  if CONSOLE then return end
  if renaming then   -- PC: typing a name
    if k == "backspace" then renameBuf = renameBuf:gsub("[\1-\127\192-\255][\128-\191]*$", "")   -- the last letter, accents included
    elseif k == "return" or k == "kpenter" then finishRename(renameBuf)
    elseif k == "escape" then renaming = nil; love.keyboard.setTextInput(false) end
    return
  end
  if KEYS[k] then press(KEYS[k]) end
end
function love.textinput(s)
  if not renaming then return end
  if CONSOLE then finishRename(s) elseif #renameBuf < 40 then renameBuf = renameBuf .. s end
end
function love.keyreleased(k) if not CONSOLE and KEYS[k] then release(KEYS[k]) end end
function love.touchpressed(_, x, y) if CONSOLE then touchDown(x, y) end end
function love.touchmoved(_, x, y) if CONSOLE then touchMove(x, y) end end
function love.touchreleased() if CONSOLE then touchUp() end end
function love.mousepressed(x, y, btn, istouch)
  if CONSOLE or istouch then return end
  if btn == 1 then touchDown(x - BOTTOM_X, y - BOTTOM_Y)
  elseif btn == 2 then rotatePiece() end
end
function love.mousemoved(x, y, _, _, istouch) if not CONSOLE and not istouch then touchMove(x - BOTTOM_X, y - BOTTOM_Y) end end
function love.mousereleased(_, _, _, istouch) if not CONSOLE and not istouch then touchUp() end end

-- ---------------------------------------------------------------- LÖVE callbacks
--[[ Loading goes one step a frame, with the step's name on both screens: if the console crashes while
     loading, the screen shows which step it was (a crash dump alone doesn't say). ]]
local BOOT = {}
-- fonts first: the system font is one 3 MB block of memory, easier to find before the textures are in
BOOT[#BOOT + 1] = { "fonts", function() for _, k in ipairs({ "tiny", "small", "body", "big" }) do fonts[k] = mkFont(k) end end }
for i = 1, A.pages do
  BOOT[#BOOT + 1] = { "texture " .. i .. "/" .. A.pages, function() pages[i] = love.graphics.newImage("gfx/atlas" .. i .. ".png") end }
end
BOOT[#BOOT + 1] = { "room", function() SALA.load() end }
BOOT[#BOOT + 1] = { "save", function()
  math.randomseed(os.time())
  load()
  P.setLang(S.lang or "en"); S.lang = P.lang()   -- English unless the player picked Portuguese (the EN|pt button)
  if not S.menu then starterMenu() end
  if not S.day then freshGame() end
  clampSel()
  syncWorld()
  buildCats()
  changed(); dirty = false
end }
BOOT[#BOOT + 1] = { "first frame", function() end }
local bootStep, bootShown = 1, false

function love.load()
  love.graphics.setDefaultFilter("nearest", "nearest")
  if love.graphics.set3D then pcall(love.graphics.set3D, false) end
end

local function drawBoot()
  love.graphics.clear(0.1, 0.05, 0.02)
  love.graphics.setColor(1, 1, 1)
  love.graphics.print("Pizza Magna " .. (D.VERSION or ""), 10, 10)
  love.graphics.print("Loading: " .. BOOT[bootStep][1] .. " (" .. bootStep .. "/" .. #BOOT .. ")", 10, 30)
end

function love.update(dt)
  if BOOT[bootStep] then
    if bootShown then BOOT[bootStep][2](); bootStep = bootStep + 1; bootShown = false end
    return
  end
  for b, left in pairs(held) do
    left = left - dt
    if left <= 0 then button(b); left = .08 end
    held[b] = left
  end
  if toasts[1] then toasts[1].time = toasts[1].time - dt; if toasts[1].time <= 0 then table.remove(toasts, 1) end end
  if armed then armed.time = armed.time - dt; if armed.time <= 0 then armed = nil end end
  if anim then updateDay(dt) end
  MUS.update(dt)
  if dirty then saveTimer = saveTimer + dt; if saveTimer > (saveFailed and 10 or 1) then save(); saveTimer = 0 end end
end

function love.draw(screen)
  if BOOT[bootStep] then drawBoot(); bootShown = true; return end
  if screen == nil then   -- PC: top screen above, bottom screen centred below
    drawTopScreen()
    love.graphics.push(); love.graphics.translate(BOTTOM_X, BOTTOM_Y)
    love.graphics.setScissor(BOTTOM_X, BOTTOM_Y, 320, 240)
    col(hex("#000000")); love.graphics.rectangle("fill", 0, 0, 320, 240)
    drawBottom()
    love.graphics.setScissor(); love.graphics.pop()
    col(hex("#000000")); love.graphics.rectangle("fill", 0, 240, BOTTOM_X, 240); love.graphics.rectangle("fill", 360, 240, 40, 240)
  elseif screen == "bottom" then drawBottom()
  else drawTopScreen() end
end

function love.quit() if dirty then save() end end

-- a Lua error is written to erro.txt in the save folder (next to save.txt) before LÖVE shows it, so it can be sent
local function logged(f)
  if not f then return nil end
  return function(...)
    local a, n = { ... }, select("#", ...)
    local ok, err = xpcall(function() return f((table.unpack or unpack)(a, 1, n)) end, debug.traceback)
    if not ok then pcall(love.filesystem.write, "erro.txt", "Pizza Magna " .. tostring(D.VERSION) .. "\n" .. tostring(err)); error(err, 0) end
  end
end
for _, k in ipairs({ "update", "draw", "gamepadpressed", "gamepadreleased", "touchpressed", "touchmoved", "touchreleased", "keypressed", "mousepressed" }) do love[k] = logged(love[k]) end
