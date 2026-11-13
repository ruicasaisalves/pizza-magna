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
local D, A, t = P.D, P.A, P.t

local CONSOLE = love._console ~= nil or love.system.getOS() == "Horizon" or love.system.getOS() == "3DS"
local BOTTOM_X, BOTTOM_Y = 40, 240   -- where the bottom screen sits in the PC window

-- text only the 3DS port has (the browser game has no buttons to explain)
local L3 = {
  en = { keys1 = "</> topping   L/R group   Up dough   Down sauce",
         keys2 = "A cut   X turn   B undo   Y clear   SELECT next screen   START quit",
         mkeys1 = "Up/Down pizza   </> price   A edit   X rename   Y remove",
         nav = "L/R or SELECT other screens   START quit", rename = "RENAME",
         dkeys = "A open the doors", drun = "</> speed   A skip to closing", rkeys = "A continue",
         ckeys = "Up/Down pizza   A enter it", skeys = "Up/Down choose   A buy / choose" },
  pt = { keys1 = "</> ingrediente   L/R grupo   Cima massa   Baixo molho",
         keys2 = "A picar   X rodar   B desfazer   Y limpar   SELECT ecrã seguinte   START sair",
         mkeys1 = "Cima/Baixo pizza   </> preço   A editar   X nome   Y remover",
         nav = "L/R ou SELECT outros ecrãs   START sair", rename = "MUDAR NOME",
         dkeys = "A abrir portas", drun = "</> velocidade   A saltar para o fecho", rkeys = "A continuar",
         ckeys = "Cima/Baixo pizza   A inscrever", skeys = "Cima/Baixo escolher   A comprar / escolher" },
}
local function l3(k) return L3[P.lang()][k] end

-- ---------------------------------------------------------------- state and save
--[[ S.name/S.editing: the pizza on the bench (no name yet = "New pizza"; editing = id of the menu pizza it came from).
     S.menu: the house menu, {id, name, dough, sauce, pieces, price}, as in the browser game. ]]
local S = { dough = "napo", sauce = "tomate", pieces = {}, sel = "fiambre", cut = "w", rot = {}, found = {}, lang = nil,
  name = nil, editing = nil, menu = nil, tab = "kitchen", msel = 1, nextId = 1, csel = 1, ssel = 1 }
local anim, report = nil, nil   -- the day running in the street; the close-of-day report on screen
local cleared = nil          -- the pizza the bin just cleared: undo on an empty bench brings it back
local dirty, saveTimer = false, 0
local toasts = {}
local an                     -- analysis of the pizza on the bench (recomputed on every change)

-- save.txt: one "key=value" a line; each menu pizza is a "pizza=" line of tab-separated fields
local function save()
  local rot = {}
  for k, v in pairs(S.rot) do rot[#rot + 1] = k .. ":" .. v end
  local lines = {
    "lang=" .. P.lang(), "dough=" .. S.dough, "sauce=" .. S.sauce, "sel=" .. S.sel, "cut=" .. S.cut,
    "rot=" .. table.concat(rot, ","), "found=" .. table.concat(S.found, ","), "pieces=" .. P.packPieces(S.pieces),
    "name=" .. (S.name or ""), "editing=" .. (S.editing or ""), "tab=" .. S.tab, "msel=" .. S.msel, "nextid=" .. S.nextId, "menu=1",
    "day=" .. S.day, "money=" .. string.format("%.2f", S.money), "rep=" .. string.format("%.4f", S.rep), "ovens=" .. S.ovens,
    "cooks=" .. S.cooks, "ads=" .. (S.ads and 1 or 0), "supplier=" .. S.supplier, "entry=" .. (S.contestEntry or ""),
    "studyweek=" .. S.studyWeek, "over=" .. (S.over and 1 or 0), "goal=" .. (S.goalDone and 1 or 0),
    "rival=" .. table.concat({ S.rival.name, S.rival.q, string.format("%.2f", S.rival.price), S.rival.promo and 1 or 0 }, "\t"),
  }
  local sales = {}
  for id, n in pairs(S.lastSales) do sales[#sales + 1] = id .. ":" .. n end
  lines[#lines + 1] = "sales=" .. table.concat(sales, ",")
  for _, n in ipairs(S.news) do
    local f = { n.k }
    for k, v in pairs(n.v) do f[#f + 1] = k .. "=" .. tostring(v):gsub("[\t\n]", " ") end
    lines[#lines + 1] = "news=" .. table.concat(f, "\t")
  end
  for _, c in ipairs(S.contestLog) do lines[#lines + 1] = "ctlog=" .. table.concat({ c.day, c.theme, c.pizza, c.pos, c.prize }, "\t") end
  for _, x in ipairs(S.tips) do lines[#lines + 1] = "tip=" .. table.concat({ x.day, x.seg, x.ing, x.combo or "" }, "\t") end
  for _, p in ipairs(S.menu) do
    lines[#lines + 1] = "pizza=" .. table.concat({ p.id, string.format("%.2f", p.price), p.dough, p.sauce, p.name, P.packPieces(p.pieces) }, "\t")
  end
  love.filesystem.write("save.txt", table.concat(lines, "\n") .. "\n")
  dirty = false
end
local function load()
  local ok, txt = pcall(love.filesystem.read, "save.txt")
  if not ok or not txt then return end
  local v, menu, news, ctlog, tips = {}, {}, {}, {}, {}
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
    elseif k then v[k] = val end
  end
  if v.menu then S.menu = menu end   -- saves from before the Menu get the starter pizzas
  if v.name and v.name ~= "" then S.name = v.name end
  if v.editing and v.editing ~= "" then S.editing = v.editing end
  if v.tab then S.tab = v.tab end
  S.msel = tonumber(v.msel) or 1
  S.nextId = tonumber(v.nextid) or 1
  if v.day then   -- saves from before the restaurant start a new game in load (S.day stays nil)
    S.day, S.money, S.rep = tonumber(v.day) or 1, tonumber(v.money) or 1000, tonumber(v.rep) or 1
    S.ovens, S.cooks, S.ads = tonumber(v.ovens) or 1, tonumber(v.cooks) or 1, v.ads == "1"
    S.supplier = D.SUPPLIER[tonumber(v.supplier)] and tonumber(v.supplier) or 1
    S.contestEntry = v.entry ~= "" and v.entry or nil
    S.studyWeek, S.over, S.goalDone = tonumber(v.studyweek) or -1, v.over == "1", v.goal == "1"
    local f = fields(v.rival or "")
    S.rival = { name = f[1] ~= "" and f[1] or "Pizza Rápida", q = tonumber(f[2]) or 52, price = tonumber(f[3]) or 7, promo = f[4] == "1" }
    S.lastSales = {}
    for id, n in (v.sales or ""):gmatch("([%w_]+):(%d+)") do S.lastSales[id] = tonumber(n) end
    S.news, S.contestLog, S.tips = news, ctlog, tips
  end
  if not ({ kitchen = 1, menu = 1, day = 1, contest = 1, shop = 1 })[S.tab] then S.tab = "kitchen" end
  if v.lang then S.lang = v.lang end
  if v.dough and D.DOUGHS[v.dough] then S.dough = v.dough end
  if v.sauce and D.SAUCES[v.sauce] then S.sauce = v.sauce end
  if v.sel and D.ING[v.sel] then S.sel = v.sel end
  if v.cut == "g" then S.cut = "g" end
  for k, n in (v.rot or ""):gmatch("([%w_]+):(%d)") do if D.ING[k] then S.rot[k] = tonumber(n) end end
  for id in (v.found or ""):gmatch("[%w_]+") do S.found[#S.found + 1] = id end
  if v.pieces and v.pieces ~= "" then pcall(function() S.pieces = P.unpackPieces(v.pieces) end) end
end

local function toast(s)   -- a new message cuts the one on screen short, so a "press again" never waits in a queue
  if toasts[1] and toasts[1].time > .6 then toasts[1].time = .6 end
  toasts[#toasts + 1] = { s = s, time = 3 }
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
  S.day, S.money, S.rep, S.ovens, S.cooks, S.ads, S.supplier = 1, 1000, 1, 1, 1, false, 1
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
  local piece = { i = S.sel, x = mid and 0 or x, y = mid and 0 or y, r = math.random() * 6.28, v = math.random(0, 2) }
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
local function pickTopping(step)
  local list = catList[catOf(S.sel)]
  local k = (idxIn(list, S.sel) - 1 + step) % #list + 1
  if list[k] ~= S.sel then S.cut = "w" end   -- a new topping starts whole
  S.sel = list[k]; dirty = true
end
local function pickCat(step)
  local k = (idxIn(D.CATS, catOf(S.sel)) - 1 + step) % #D.CATS + 1
  S.sel = catList[D.CATS[k]][1]; S.cut = "w"; dirty = true
end
local function cycle(order, cur, step) return order[(idxIn(order, cur) - 1 + step) % #order + 1] end
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
--[[ On the 3DS each new font copies the whole system font (about 3 MB), and four of them crashed the console
     while loading. There the game uses only the default font, scaled to each size. On a PC each size is
     its own font (PM3DS_ONEFONT=1 tries the console way). ]]
local ONE_FONT = CONSOLE or (os.getenv and os.getenv("PM3DS_ONEFONT") ~= nil)
local function mkFont(size)
  if ONE_FONT then
    local f = love.graphics.getFont()
    pcall(f.setFilter, f, "linear", "linear")   -- scaled down with "nearest", thin letters (i, l) lost whole columns
    return { f = f, s = size * 1.2 / f:getHeight() }   -- getHeight is the line, about 1.2 times the size
  end
  return { f = love.graphics.newFont(size), s = 1 }
end
local function fw(font, s) local F = fonts[font]; return F.f:getWidth(s) * F.s end   -- width in pixels
local function fprint(font, s, x, y) local F = fonts[font]; love.graphics.setFont(F.f); love.graphics.print(s, x, y, 0, F.s, F.s) end
local function text(s, x, y, font, c, align, w)
  local F = fonts[font]
  love.graphics.setFont(F.f); col(c)
  if align then love.graphics.printf(s, x, y, w / F.s, align, 0, F.s, F.s) else love.graphics.print(s, x, y, 0, F.s, F.s) end
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
local BW, OY, PX, PY = 320, 22, 12, 37
local PCX, PCY = PX + PR, PY + PR
local BOWLS = { { g = 0, x = 227, y = 26 }, { g = 1, x = 227, y = 94 } }
local BOWL_W, BOWL_H = 58, 40
local LANG_BTN = { x = 272, y = 224, w = 44, h = 14 }

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
  h = h or 14
  w = w or math.ceil(fw("tiny", label)) + 10
  col(hex("#4a260f")); love.graphics.rectangle("fill", x, y, w, h)
  col(danger and hex("#e0603c") or C.gold); love.graphics.rectangle("fill", x + 1, y + 1, w - 2, h - 2)
  col(danger and hex("#f59a7c") or hex("#fbe39a")); love.graphics.rectangle("fill", x + 1, y + 1, w - 2, 1)
  benchLabel(label, x + w / 2, y + math.floor((h - 10) / 2), hex("#3a2706"), danger and hex("#f59a7c", .8) or hex("#fbe39a", .8))
  hit(x, y, w, h, fn)
  return x + w
end
local function langBtn()
  local L = LANG_BTN
  plateBtn(P.lang() == "pt" and "PT|en" or "EN|pt", L.x, L.y, function() setLang(P.lang() == "pt" and "en" or "pt") end, L.w, L.h)
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

local function drawKitchenBottom()
  marble()
  pizzaOnMarble(S)
  nameStrip(S.name or t("k.newname"))
  hit(0, 0, BW, OY, renameDraft)
  -- right side: name plate and two bowls (whole / chopped)
  local sel, cut = S.sel, curCut()
  love.graphics.push(); love.graphics.translate(0, OY)
  local cx = BOWLS[1].x + BOWL_W / 2
  local label = P.upper(P.ingName(sel))
  local hw = math.min(BW - cx - 3, math.max(46, math.ceil(fw("tiny", label) / 2) + 6))
  col(hex("#4a260f")); love.graphics.rectangle("fill", cx - hw, 6, hw * 2, 13)
  col(C.gold); love.graphics.rectangle("fill", cx - hw + 1, 7, hw * 2 - 2, 11)
  col(hex("#fbe39a")); love.graphics.rectangle("fill", cx - hw + 1, 7, hw * 2 - 2, 1)
  benchLabel(fitText(label, "tiny", hw * 2 - 4), cx, 7, hex("#3a2706"), hex("#fbe39a", .8))
  for _, b in ipairs(BOWLS) do
    local on, ok = b.g == cut, b.g == 0 or P.canGrate(sel)
    local bx, by = b.x + BOWL_W / 2, b.y + 13
    if on then
      pxRect(b.x - 5, b.y - 4, BOWL_W + 10, BOWL_H + 18, hex("#3a2706"))
      pxRect(b.x - 4, b.y - 3, BOWL_W + 8, BOWL_H + 16, C.gold)
      pxRect(b.x - 3, b.y - 2, BOWL_W + 6, BOWL_H + 14, hex("#94661a"))
    end
    spr("bowl", bx, b.y + BOWL_H / 2)
    if ok then
      local f0 = A.frames[sel .. "_0"]
      if b.g == 0 and P.canRotate(sel) then sprFit(P.wholeKey(sel, 0, curAng()), bx, by + 1, 44)
      elseif b.g == 1 and P.BIG_SHRED[sel] then sprFit(sel .. "_g0", bx, by + 2, 46)   -- the big cheese handful
      elseif b.g == 0 and f0 and f0[4] > 36 then sprFit(sel .. "_0", bx, by + 1, 40)   -- one big piece fills the bowl
      else
        local k = b.g == 1 and "_g" or "_"
        spr(sel .. k .. 1, bx - 9, by - 1); spr(sel .. k .. 2, bx + 9, by); spr(sel .. k .. 0, bx, by + 2)
      end
    end
    local key = b.g == 0 and "bench.whole" or (ok and (P.isCheese(sel) and "bench.grated" or "bench.chopped") or "bench.nograte." .. P.noCutKind(sel))
    benchLabel(t(key), bx, b.y + BOWL_H + 3, on and C.ink or hex("#6c5233"))
  end
  -- the little LCD: cost, pieces, weight
  local lx, ly, lw = BOWLS[1].x - 13, 154, BOWL_W + 26
  col(hex("#2a1407")); love.graphics.rectangle("fill", lx - 2, ly - 2, lw + 4, 44)
  col(hex("#081008")); love.graphics.rectangle("fill", lx, ly, lw, 40)
  col(C.lcd)
  local rows = { { "bench.c", P.eur(an.cost) }, { "bench.n", tostring(#S.pieces) }, { "bench.w", P.fmtG(P.pizzaGrams(S)) } }
  for k, r in ipairs(rows) do
    local y = ly + 3 + (k - 1) * 12
    fprint("tiny", t(r[1]), lx + 3, y)
    fprint("tiny", r[2], lx + lw - 3 - fw("tiny", r[2]), y)
  end
  love.graphics.pop()
  -- the strip at the bottom: new pizza, save to the menu, the menu, language
  local x = plateBtn(P.upper(t("k.fresh")), 4, 224, newDraft, nil, nil, isArmed("new"))
  x = plateBtn(P.upper(t(S.editing and "k.save.edit" or "k.save.new")), x + 4, 224, savePizza)
  plateBtn(P.upper(t("nav.menu")), x + 4, 224, function() S.tab = "menu"; clampSel(); dirty = true end)
  langBtn()
end

-- ---------------------------------------------------------------- bottom screen: the chosen menu pizza
local function lcd(x, y, w, rows)
  local h = #rows * 12 + 4
  col(hex("#2a1407")); love.graphics.rectangle("fill", x - 2, y - 2, w + 4, h + 4)
  col(hex("#081008")); love.graphics.rectangle("fill", x, y, w, h)
  for k, r in ipairs(rows) do
    local yy = y + 3 + (k - 1) * 12
    col(C.lcd); fprint("tiny", r[1], x + 3, yy)
    col(r[3] or C.lcd); fprint("tiny", r[2], x + w - 3 - fw("tiny", r[2]), yy)
  end
end
local function drawMenuBottom()
  marble()
  local p = selPizza()
  local strip = function()
    local x = plateBtn(P.upper(t("nav.cozinha")), 4, 224, function() S.tab = "kitchen"; dirty = true end)
    plateBtn(P.upper(t("k.fresh")), x + 4, 224, newDraft, nil, nil, isArmed("new"))
    langBtn()
  end
  if not p then   -- the "+ Create new pizza" row (or an empty menu)
    if #S.menu == 0 then text(t("menu.empty"), 20, 60, "body", C.ink, "center", 280) end
    plateBtn(P.upper(t("menu.new", { n = #S.menu })), 60, 130, newDraft, 200, 24)
    strip(); return
  end
  local a = anOf(p)
  pizzaOnMarble(p)
  nameStrip(p.name)
  hit(0, 0, BW, OY, renamePizza)
  -- right column: price with - and +, the figures, edit / rename / remove
  local rx, rw = 222, 94
  plateBtn("-", rx, 30, function() priceStep(-.5) end, 18, 22)
  plateBtn("+", rx + rw - 18, 30, function() priceStep(.5) end, 18, 22)
  text(P.eur(p.price), rx + 18, 33, "body", C.ink, "center", rw - 36)
  local margin = p.price - a.cost
  lcd(rx, 62, rw, {
    { fitText(P.upper(t("k.q")), "tiny", 60), tostring(a.q), P.qColor(a.q) },
    { t("bench.c"), P.eur(a.cost) },
    { fitText(P.upper(t("menu.margin")), "tiny", 50), P.eur(margin), margin > 0 and C.good or C.bad },
  })
  plateBtn(P.upper(t("menu.edit")), rx, 114, editPizza, rw, 18)
  plateBtn(l3("rename"), rx, 138, renamePizza, rw, 18)
  plateBtn(fitText(P.upper(t(isArmed("remove") and "menu.confirm" or "menu.remove")), "tiny", rw - 6), rx, 162, removePizza, rw, 18, isArmed("remove"))
  strip()
end

local drawBottom   -- (defined with the other screens)

-- ---------------------------------------------------------------- top screen: picker and analysis
local function meter(x, y, w, h, v, c)
  col(hex("#000000", .45)); love.graphics.rectangle("fill", x, y, w, h)
  col(c); love.graphics.rectangle("fill", x, y, math.floor(w * v / 100 + .5), h)
end

local drawHeader
-- the screens, in the order SELECT goes through them, and the header that names them
local TABS = { "kitchen", "menu", "day", "contest", "shop" }
local TAB_KEY = { kitchen = "nav.cozinha", menu = "nav.menu", day = "nav.dia", contest = "nav.concurso", shop = "nav.loja" }
local function goTab(step)
  if anim or report then return end   -- the day runs to its end, and its report is read first
  local k = (idxIn(TABS, S.tab) - 1 + step) % #TABS + 1
  S.tab = TABS[k]; armed = nil; clampSel(); dirty = true
end
local function stars(r) return string.format(P.lang() == "pt" and "%.1f" or "%.1f", r):gsub("%.", P.lang() == "pt" and "," or ".") .. "*" end
drawHeader = function()
  col(C.panel); love.graphics.rectangle("fill", 0, 0, 400, 18)
  local x = 6
  for _, tb in ipairs(TABS) do
    local s = P.upper(t(TAB_KEY[tb]))
    local on = tb == S.tab
    text(s, x, 4, "tiny", on and C.gold or C.dim)
    if on then col(C.gold); love.graphics.rectangle("fill", x, 15, fw("tiny", s), 1) end
    x = x + fw("tiny", s) + 9
  end
  text(P.eur(S.money) .. "   " .. stars(S.rep), 200, 3, "small", S.money < 0 and C.bad or C.cream, "right", 194)
end

local function drawTop()
  col(C.bg); love.graphics.rectangle("fill", 0, 0, 400, 240)
  drawHeader()
  -- left: the topping picker
  local cat = catOf(S.sel)
  local list = catList[cat]
  local k = idxIn(list, S.sel)
  -- the groups as tabs with their symbols (as on phones): L/R change group, the open one is light and raised
  col(C.panel); love.graphics.rectangle("fill", 6, 20, 188, 20)
  text("L", 8, 25, "small", C.dim); text("R", 6, 25, "small", C.dim, "right", 186)
  for i, c in ipairs(D.CATS) do
    local tx = 18 + (i - 1) * 24
    if c == cat then
      col(hex("#f3e6c6")); love.graphics.rectangle("fill", tx, 20, 23, 20)
      pxRect(tx, 20, 23, 20, C.gold)
      spr("cat_" .. c, tx + 11.5, 30)
    else
      col(hex("#7a4520")); love.graphics.rectangle("fill", tx + 1, 23, 21, 16)
      spr("cat_" .. c, tx + 11.5, 31, .7)
    end
  end
  for s = -2, 2 do
    local id = list[(k - 1 + s) % #list + 1]
    local cx, cy = 100 + s * 38, 58
    col(hex(s == 0 and "#4a260f" or "#1a0d05")); love.graphics.rectangle("fill", cx - 17, cy - 17, 34, 34)
    if s == 0 then pxRect(cx - 18, cy - 18, 36, 36, C.gold) end
    sprFit(P.wholeKey(id, 0, 0), cx, cy, 31)
  end
  text(P.ingName(S.sel), 6, 80, "body", C.cream, "center", 188)
  local cutL = curCut() == 1 and t(P.isCheese(S.sel) and "bench.grated" or "bench.chopped") or t("bench.whole")
  text(P.eur(P.ingC(S.sel)) .. " · " .. cutL, 6, 97, "small", C.dim, "center", 188)
  col(C.panel); love.graphics.rectangle("fill", 6, 116, 188, 38)
  text(t("k.dough") .. ":", 10, 120, "small", C.dim); text(t("dough." .. S.dough), 70, 120, "small", C.cream)
  text(t("k.sauce") .. ":", 10, 137, "small", C.dim); text(t("sauce." .. S.sauce), 70, 137, "small", C.cream)
  -- notes
  local y = 160
  if an.n == 0 then
    text(t("k.empty"), 6, y, "small", C.dim, "left", 188)
  else
    for i = 1, math.min(4, #an.notes) do
      local nt = an.notes[i]
      text(fitText(nt[2], "small", 188), 6, y, "small", nt[1] == "good" and C.good or nt[1] == "combo" and C.combo or C.bad)
      y = y + 14
    end
  end
  -- right: quality, cost, appeal
  local rx = 206
  col(C.panel); love.graphics.rectangle("fill", rx - 4, 22, 196, 196)
  local qc = P.qColor(an.q)
  text(t("k.q"), rx, 26, "small", C.dim)
  text(tostring(an.q), rx, 38, "big", qc)
  meter(rx + 52, 48, 130, 8, an.q, qc)
  text(t("k.cost"), rx, 72, "small", C.dim)
  text(P.eur(an.cost), rx, 86, "body", C.cream)
  local nStr = tostring(an.n); if P.lang() == "pt" then nStr = nStr:gsub("%.", ",") end
  text(fitText(t("k.portions", { n = nStr, p = P.eur(P.suggestPrice(an.cost)) }), "small", 186), rx, 104, "small", C.dim)
  text(fitText(t("k.appeal"), "small", 186), rx, 124, "small", C.dim)
  for i, sk in ipairs(D.SEG_ORDER) do
    local yy = 140 + (i - 1) * 18
    text(fitText(t("seg." .. sk), "small", 70), rx, yy, "small", C.cream)
    meter(rx + 74, yy + 3, 88, 8, an.appeal[sk], hex(D.SEG[sk].col))
    text(tostring(an.appeal[sk]), rx + 166, yy, "small", C.cream)
  end
  -- buttons
  text(l3("keys1"), 0, 214, "tiny", C.dim, "center", 400)
  text(l3("keys2"), 0, 226, "tiny", C.dim, "center", 400)
end

-- a menu pizza drawn small (the whole 170 px pizza scaled)
local function miniPizza(p, cx, cy, size)
  love.graphics.push(); love.graphics.translate(cx, cy); love.graphics.scale(size / A.pizza)
  drawPizza(p, 0, 0)
  love.graphics.pop()
end
local ROW_H, ROWS = 34, 5
local function drawMenuTop()
  col(C.bg); love.graphics.rectangle("fill", 0, 0, 400, 240)
  drawHeader()
  local sp = selPizza()
  local loss = sp and sp.price < anOf(sp).cost
  local lead = t("menu.house") .. " (" .. #S.menu .. ")  ·  " .. t("k.book", { n = #S.found, t = #D.COMBOS })
  text(fitText(loss and t("menu.loss", { x = P.eur(anOf(sp).cost - sp.price) }) or lead, "small", 388), 6, 21, "small", loss and C.bad or C.dim)
  local n = #S.menu + 1
  local first = math.max(1, math.min(S.msel - 2, n - ROWS + 1))
  for row = 0, ROWS - 1 do
    local k = first + row
    if k > n then break end
    local y = 38 + row * ROW_H
    local on = k == S.msel
    col(on and hex("#4a260f") or C.panel); love.graphics.rectangle("fill", 6, y, 388, ROW_H - 3)
    if on then pxRect(5, y - 1, 390, ROW_H - 1, C.gold) end
    local p = S.menu[k]
    if p then
      local a = anOf(p)
      miniPizza(p, 24, y + 15, 28)
      text(fitText(p.name, "body", 200), 44, y + 1, "body", C.cream)
      text(fitText(t("dough." .. p.dough) .. " · " .. t("sauce." .. p.sauce), "tiny", 200), 44, y + 18, "tiny", C.dim)
      text(P.eur(p.price), 250, y + 1, "body", C.gold, "right", 138)
      local margin = p.price - a.cost
      text("Q" .. a.q, 250, y + 18, "tiny", P.qColor(a.q))
      text(t("menu.margin") .. " " .. P.eur(margin), 280, y + 18, "tiny", margin > 0 and C.good or C.bad, "right", 108)
    else
      text(t("menu.new", { n = #S.menu }), 6, y + 8, "body", on and C.gold or C.dim, "center", 388)
    end
  end
  text(l3("mkeys1"), 0, 214, "tiny", C.dim, "center", 400)
  text(l3("nav"), 0, 226, "tiny", C.dim, "center", 400)
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
local SEGC = {}
for _, k in ipairs(D.SEG_ORDER) do SEGC[k] = hex(D.SEG[k].col) end
local DOOR_OURS, DOOR_RIVAL, WALK = 86, 238, 70   -- door positions in the street, walking speed (px/s at x1)
local function startDay()
  if anim or report then return end
  if #S.menu == 0 then toast(t("ct.need")); return end
  syncWorld()
  anim = { res = G.simulateDay(S), t = 0, speed = 1, idx = 1, cnt = { served = 0, rival = 0, left = 0, rev = 0 }, walkers = {}, bubbles = {} }
end
local function endDay()
  local a = anim
  anim = nil
  report = G.finishDay(S, a.res)
  syncWorld(); save()
end
local function arrive(w)   -- a customer reaches a door: the counters move then
  local e, c = w.e, anim.cnt
  if e.target == "ours" then
    if e.out == "happy" or e.out == "meh" then
      c.served = c.served + 1; c.rev = c.rev + e.price
      anim.bubbles[#anim.bubbles + 1] = { x = w.x, y = 150, s = "+" .. P.eur(e.price), c = e.out == "happy" and C.good or C.combo, life = 1.2 }
    else
      c.left = c.left + 1
      anim.bubbles[#anim.bubbles + 1] = { x = w.x, y = 150, s = "x", c = C.bad, life = 1.2 }
    end
  elseif e.target == "rival" then c.rival = c.rival + 1 end
end
local function updateDay(dt)
  local a = anim
  local DS = D.DAY_SECONDS
  a.t = a.t + dt * a.speed
  local ev = a.res.events
  while ev[a.idx] and ev[a.idx].t * DS <= a.t do   -- a new customer comes down the street, from either side
    local e = ev[a.idx]
    local left = math.random() < .5
    local tx = e.target == "ours" and DOOR_OURS or e.target == "rival" and DOOR_RIVAL or (left and 340 or -20)
    a.walkers[#a.walkers + 1] = { e = e, x = left and -8 or 328, y = 178 + math.random() * 14, tx = tx, step = 0 }
    a.idx = a.idx + 1
  end
  for k = #a.walkers, 1, -1 do
    local w = a.walkers[k]
    local d = WALK * dt * a.speed
    w.step = w.step + d
    if math.abs(w.tx - w.x) <= d then
      if w.e.target ~= "none" then arrive(w) end
      table.remove(a.walkers, k)
    else w.x = w.x + (w.tx > w.x and d or -d) end
  end
  for k = #a.bubbles, 1, -1 do
    local b = a.bubbles[k]
    b.life = b.life - dt * a.speed; b.y = b.y - dt * a.speed * 14
    if b.life <= 0 then table.remove(a.bubbles, k) end
  end
  if a.idx > #ev and #a.walkers == 0 and a.t >= DS * .92 then endDay() end
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
  local share = (c.served + c.rival > 0) and (math.floor(c.served / (c.served + c.rival) * 100 + .5) .. "%") or "--"
  local rep = string.format("%.1f", S.rep); if P.lang() == "pt" then rep = rep:gsub("%.", ",") end
  return {
    { t("lcd.day") .. " " .. S.day .. " " .. P.upper(G.weekday(S.day)), clock },
    { t("lcd.pop"), rep .. "/5" },
    { a and t("lcd.street") or t("lcd.exp"), a and tostring(#a.res.events - a.idx + 1 + #a.walkers) or ("~" .. G.expected(S)) },
    { t("lcd.served"), tostring(c.served) },
    { t("lcd.rival"), tostring(c.rival) },
    { t("lcd.left"), tostring(c.left) },
    { t("lcd.share"), share },
    false,
    { t("lcd.cooks"), tostring(S.cooks) },
    { t("lcd.ovens"), tostring(S.ovens) },
    { t("lcd.tables"), D.ROOM.tables .. " · " .. D.ROOM.seats },
    { t("lcd.cap"), c.served .. "/" .. G.capacity(S) },
    { t("lcd.rv"), (S.rival.promo and "2X1 " or "") .. P.eur(S.rival.price) },
    false,
    { t("lcd.rev"), P.eur(c.rev) },
    { t("lcd.cash"), P.eur(S.money) },
  }
end
local function drawDayTop()
  col(C.bg); love.graphics.rectangle("fill", 0, 0, 400, 240)
  drawHeader()
  -- the LCD
  col(hex("#2a1407")); love.graphics.rectangle("fill", 4, 22, 196, 178)
  col(hex("#081008")); love.graphics.rectangle("fill", 6, 24, 192, 174)
  local y = 27
  for _, r in ipairs(lcdRows()) do
    if r then
      text(fitText(r[1], "tiny", 130), 10, y, "tiny", C.lcd)
      text(r[2], 10, y, "tiny", C.lcd, "right", 184)
      y = y + 11
    else
      col(C.lcd, .35); love.graphics.rectangle("fill", 10, y + 4, 184, 1); y = y + 9
    end
  end
  -- right: contest today, news, the manager's notes
  local x, w = 206, 190
  y = 22
  if S.day % 5 == 0 then
    local entry
    for _, p in ipairs(S.menu) do if p.id == S.contestEntry then entry = p end end
    local s = "> " .. t("day.ban", { x = P.upper(t("th." .. G.themeFor(S.day))) }) .. " " ..
      (entry and t("day.ban.in", { p = P.upper(entry.name) }) or t("day.ban.none"))
    col(hex("#4a260f")); love.graphics.rectangle("fill", x - 2, y, w + 4, 38)
    text(s, x + 2, y + 2, "tiny", C.combo, "left", w - 4)
    y = y + 42
  end
  text(t("day.news"), x, y, "small", C.gold); y = y + 15
  local notes = {}
  if D.ROOM.seats * 3 < G.expected(S) then notes[#notes + 1] = t("day.seats") end
  if G.capacity(S) < G.expected(S) * .6 then notes[#notes + 1] = t("day.queue") end
  local lines = {}
  for _, n in ipairs(S.news) do lines[#lines + 1] = { G.newsText(n), C.cream } end
  for _, n in ipairs(notes) do table.insert(lines, 1, { t("day.warn") .. ": " .. n, C.bad }) end
  local F = fonts.tiny
  for _, l in ipairs(lines) do
    local _, wrapped = F.f:getWrap(l[1], (w - 4) / F.s)
    local h = #wrapped * F.f:getHeight() * F.s
    if y + h > 200 then break end
    text(l[1], x, y, "tiny", l[2], "left", w - 4)
    y = y + h + 3
  end
  -- who the colours are, centred under both columns
  local lw = 0
  for _, k in ipairs(D.SEG_ORDER) do lw = lw + 20 + fw("tiny", t("seg." .. k)) end
  local lx = math.floor(200 - lw / 2)
  for _, k in ipairs(D.SEG_ORDER) do
    col(SEGC[k]); love.graphics.rectangle("fill", lx, 205, 6, 6)
    local s = t("seg." .. k)
    text(s, lx + 9, 203, "tiny", C.dim)
    lx = lx + 20 + fw("tiny", s)
  end
  text((anim and l3("drun") or l3("dkeys")) .. "   " .. l3("nav"), 0, 222, "tiny", C.dim, "center", 400)
end

-- the street: our pizzeria and the rival's, and the people walking by
local function shopFront(x, w, name, wall, awning, sign)
  col(wall); love.graphics.rectangle("fill", x, 46, w, 124)
  for k = 0, 5 do col(k % 2 == 0 and awning or hex("#f6e7c8")); love.graphics.rectangle("fill", x + k * w / 6, 70, w / 6, 12) end
  col(hex("#1a0d05")); love.graphics.rectangle("fill", x + 8, 50, w - 16, 16)
  text(fitText(P.upper(name), "tiny", w - 20), x + 8, 53, "tiny", sign, "center", w - 16)
  col(hex("#9fd3e8")); love.graphics.rectangle("fill", x + 8, 94, 34, 34); love.graphics.rectangle("fill", x + w - 42, 94, 34, 34)
  col(hex("#3a2213")); love.graphics.rectangle("fill", x + w / 2 - 12, 128, 24, 42)
  col(C.gold); love.graphics.rectangle("fill", x + w / 2 + 6, 148, 3, 3)
end
local function drawStreet()
  col(hex("#7fb6d6")); love.graphics.rectangle("fill", 0, 0, 320, 170)
  col(hex("#a7c9de")); love.graphics.rectangle("fill", 0, 0, 320, 20)
  shopFront(DOOR_OURS - 66, 132, "Pizza Magna", hex("#c96f3b"), hex("#2f8f4e"), C.gold)
  shopFront(DOOR_RIVAL - 60, 120, S.rival.name, hex("#8d8f96"), hex("#c4352a"), hex("#ff8a6a"))
  col(hex("#b9a58a")); love.graphics.rectangle("fill", 0, 170, 320, 30)
  col(hex("#9c8a72")); for x = 0, 320, 20 do love.graphics.rectangle("fill", x, 170, 1, 30) end
  col(hex("#4a4a50")); love.graphics.rectangle("fill", 0, 200, 320, 24)
  col(hex("#d9d9d9")); for x = 4, 320, 28 do love.graphics.rectangle("fill", x, 211, 14, 2) end
  if not anim then return end
  table.sort(anim.walkers, function(a, b) return a.y < b.y end)
  for _, w in ipairs(anim.walkers) do   -- a little person: legs that step, body in the group's colour, head
    local x, y = math.floor(w.x), math.floor(w.y)
    local leg = math.floor(w.step / 4) % 2
    col(hex("#2a1a10")); love.graphics.rectangle("fill", x - 2, y - 4, 2, 4 - leg); love.graphics.rectangle("fill", x + 1, y - 4, 2, 3 + leg)
    col(SEGC[w.e.seg]); love.graphics.rectangle("fill", x - 3, y - 12, 7, 8)
    col(hex("#f1c7a0")); love.graphics.rectangle("fill", x - 2, y - 17, 5, 5)
    col(hex("#2b1b10")); love.graphics.rectangle("fill", x - 2, y - 18, 5, 2)
  end
  for _, b in ipairs(anim.bubbles) do
    local w = fw("tiny", b.s) + 6
    col(hex("#000000", .7)); love.graphics.rectangle("fill", b.x - w / 2, b.y, w, 12)
    text(b.s, b.x - w / 2, b.y + 1, "tiny", b.c, "center", w)
  end
end
local function drawDayBottom()
  drawStreet()
  if anim then
    local x = 4
    for _, v in ipairs({ 1, 2, 4 }) do
      x = plateBtn("x" .. v, x, 224, function() anim.speed = v end, 28, 14, anim.speed == v) + 4
    end
    plateBtn(P.upper(t("run.skip")), x, 224, skipDay)
  else
    plateBtn(fitText(P.upper(t("day.open", { d = S.day })), "tiny", 300), 20, 196, startDay, 280, 24)
    langBtn()
  end
end

-- the close of the day
local function drawReportTop()
  col(C.bg); love.graphics.rectangle("fill", 0, 0, 400, 240)
  drawHeader()
  local r, res = report, report.res
  text(t("rep.close", { d = r.day, w = G.weekday(r.day) }), 8, 22, "small", C.dim)
  text(t(r.profit >= 0 and "rep.good" or "rep.bad") .. ": " .. P.eur(r.profit), 8, 36, "body", r.profit >= 0 and C.good or C.bad)
  local rows = {
    { t("rep.served"), t("rep.ofN", { n = res.served, N = res.N }) },
    { t("rep.rival", { x = S.rival.name }), tostring(res.toRival) },
    { t("rep.full"), tostring(res.full) },
    { t("rep.noseat"), tostring(res.noseat) },
    { t("rep.happy"), res.happy .. " / " .. res.unhappy },
  }
  local money = {
    { t("rep.revenue"), P.eur(res.revenue) },
    { t("rep.ing"), P.eur(-res.ingCost) },
    { t("rep.rent"), P.eur(-D.RENT) },
    { t("rep.sal"), P.eur(-r.sal) },
    { t("rep.result"), P.eur(r.profit), r.profit >= 0 and C.good or C.bad },
  }
  for k, row in ipairs(rows) do
    local y = 60 + (k - 1) * 15
    text(fitText(row[1], "small", 180 - fw("small", row[2])), 8, y, "small", C.cream); text(row[2], 8, y, "small", C.cream, "right", 186)
  end
  for k, row in ipairs(money) do
    local y = 60 + (k - 1) * 15
    text(row[1], 208, y, "small", row[3] or C.cream); text(row[2], 208, y, "small", row[3] or C.cream, "right", 186)
  end
  local f = function(v) local s = string.format("%.2f", v); return P.lang() == "pt" and s:gsub("%.", ",") or s end
  text(t("rep.rep") .. ": " .. f(r.repBefore) .. " -> " .. f(r.repAfter) .. "*", 8, 140, "small", C.gold)
  local w = P.week(S.day)
  local wk = t("wk.ing", { x = P.ingName(w.ing) }) .. "  " .. t("wk.low", { x = P.ingName(w.low) }) .. "  " ..
    t("wk.combo", { x = t("combo." .. w.combo), r = G.comboReq(w.combo) })
  col(hex("#4a260f")); love.graphics.rectangle("fill", 6, 158, 388, 50)
  text(wk, 10, 161, "tiny", C.combo, "left", 380)
  text(l3("rkeys"), 0, 220, "tiny", C.dim, "center", 400)
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
    plateBtn(P.upper(t("end.again")), 60, 180, closeReport, 200, 24)
    return
  end
  local y = 6
  if r.goal then
    text(t("goal.title") .. " " .. t("goal.lead", { m = P.eur(S.money), r = string.format("%.1f", S.rep), d = r.day }), 8, y, "tiny", hex("#1f7a3a"), "left", 304)
    y = y + 34
  end
  local F = fonts.tiny
  for _, q in ipairs(r.quotes) do
    local s = t("seg." .. q[1]) .. ": “" .. q[2] .. "”"
    local _, wrapped = F.f:getWrap(s, 304 / F.s)
    text(s, 8, y, "tiny", C.ink, "left", 304)
    y = y + #wrapped * F.f:getHeight() * F.s + 4
  end
  local c = r.contest
  if c then
    y = y + 2
    text(t("ct.res", { t = t("th." .. c.th), n = c.pos }) .. (c.prize > 0 and (" · +" .. P.eur(c.prize)) or ""), 8, y, "small", hex("#8a5a00")); y = y + 14
    if c.dq then text(t("ct.dq", { x = c.dq }), 8, y, "tiny", C.bad); y = y + 11 end
    for k, x in ipairs(c.rows) do
      local cc = x.me and hex("#8a5a00") or C.ink
      text(k .. ". " .. fitText(x.n, "tiny", 250), 12, y, "tiny", cc); text(tostring(x.s), 12, y, "tiny", cc, "right", 296); y = y + 11
    end
  end
  local res = r.res
  local tip = res.noseat > 3 and "rep.tip.seats" or res.full > 3 and "rep.tip.queue" or res.toRival > res.served and "rep.tip.rival" or nil
  if tip and y < 180 then text(t(tip), 8, math.max(y + 2, 174), "tiny", hex("#6c5233"), "left", 304) end
  plateBtn(P.upper(t("rep.go")), 90, 206, closeReport, 140, 24)
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
  col(C.panel); love.graphics.rectangle("fill", 6, 88, 192, 80)
  for k, r in ipairs(rows) do
    local y = 91 + (k - 1) * 15
    text(fitText(r[1], "small", 178 - fw("small", r[2])), 10, y, "small", C.dim); text(r[2], 10, y, "small", C.cream, "right", 184)
  end
  col(C.panel); love.graphics.rectangle("fill", 202, 88, 192, 120)
  text(t("ct.hist"), 206, 91, "small", C.gold)
  if #S.contestLog == 0 then text(t("ct.none"), 206, 107, "tiny", C.dim, "left", 184) end
  for k, l in ipairs(S.contestLog) do
    if k > 4 then break end
    local y = 106 + (k - 1) * 25
    text(fitText(t("ct.histrow", { d = l.day, t = t("th." .. l.theme) }), "tiny", 184), 206, y, "tiny", C.cream)
    text(fitText(l.pizza, "tiny", 110), 206, y + 11, "tiny", C.dim)
    text(t("ct.place", { n = l.pos }) .. (l.prize > 0 and (" · " .. P.eur(l.prize)) or ""), 206, y + 11, "tiny", C.combo, "right", 184)
  end
  text(t("ct.judge", { d = cd }), 8, 174, "tiny", C.dim, "left", 190)
  text(l3("ckeys"), 0, 214, "tiny", C.dim, "center", 400)
  text(l3("nav"), 0, 226, "tiny", C.dim, "center", 400)
end
local function drawContestBottom()
  col(hex("#f3ead3")); love.graphics.rectangle("fill", 0, 0, 320, 240)
  text(t("ct.pick"), 8, 4, "small", C.ink)
  text(fitText(t(S.contestEntry and "ct.swap" or "ct.pay"), "tiny", 304), 8, 19, "tiny", hex("#6c5233"))
  if #S.menu == 0 then text(t("ct.need"), 8, 60, "body", C.ink, "center", 304); langBtn(); return end
  S.csel = math.max(1, math.min(S.csel, #S.menu))
  local th = G.themeFor(G.nextContestDay(S))
  local RH, N = 30, 6
  local first = math.max(1, math.min(S.csel - 2, #S.menu - N + 1))
  for row = 0, N - 1 do
    local k = first + row
    local p = S.menu[k]
    if not p then break end
    local y = 34 + row * RH
    local on, entered = k == S.csel, p.id == S.contestEntry
    col(entered and hex("#e3b34a") or on and hex("#eadcb8") or hex("#f9f3e3")); love.graphics.rectangle("fill", 6, y, 308, RH - 3)
    if on then pxRect(5, y - 1, 310, RH - 1, hex("#4a260f")) end
    miniPizza(p, 22, y + 13, 24)
    local sc = P.contestScore(th, p)
    text(fitText((entered and "> " or "") .. p.name, "small", 170), 40, y + 2, "small", C.ink)
    text(sc.dq and t("ct.dq", { x = sc.dq }) or t("ct.pre", { n = math.floor(sc.s + .5) }), 40, y + 15, "tiny", sc.dq and hex("#b0381c") or hex("#6c5233"))
    hit(6, y, 308, RH - 3, function() S.csel = k; enterContest(p) end)
  end
  langBtn()
end

-- ---------------------------------------------------------------- the shop
local SHOP_ROWS = { "oven", "cook", "ads", "supplier", "study", "reset" }
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
  elseif id == "reset" then resetGame() end
end
local function shopRow(id)   -- name, state, price
  local it = shopItem(id)
  if it then return t("shop." .. id), it.lvl(S), it.ok(S) and P.eur(it.cost(S)) or t("shop.done") end
  if id == "supplier" then return t("sup.title"), t("sup." .. S.supplier), "" end
  if id == "study" then return t("study.title"), S.studyWeek == G.weekOf(S.day) and t("study.done") or "", P.eur(D.STUDY_COST) end
  return t("shop.reset"), "", ""
end
local function drawShopTop()
  col(C.bg); love.graphics.rectangle("fill", 0, 0, 400, 240)
  drawHeader()
  text(fitText(t("shop.lead", { m = P.eur(S.money) }), "small", 388), 6, 21, "small", C.dim)
  S.ssel = math.max(1, math.min(S.ssel, #SHOP_ROWS))
  for k, id in ipairs(SHOP_ROWS) do
    local y = 38 + (k - 1) * 24
    local on = k == S.ssel
    col(on and hex("#4a260f") or C.panel); love.graphics.rectangle("fill", 6, y, 388, 21)
    if on then pxRect(5, y - 1, 390, 23, C.gold) end
    local n, l, c = shopRow(id)
    text(n, 12, y + 4, "small", id == "reset" and C.bad or C.cream)
    text(l, 180, y + 5, "tiny", C.dim)
    text(c, 12, y + 4, "small", C.gold, "right", 376)
  end
  text(l3("skeys"), 0, 214, "tiny", C.dim, "center", 400)
  text(l3("nav"), 0, 226, "tiny", C.dim, "center", 400)
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
    text(it.lvl(S), 10, 70, "small", C.ink)
    local ok = it.ok(S)
    local lbl = ok and (P.upper(t("shop.buy")) .. "  " .. P.eur(it.cost(S))) or P.upper(t("shop.done"))
    plateBtn(lbl, 10, 96, function() buyItem(it) end, 150, 24, ok and S.money < it.cost(S))
    if id == "cook" and S.cooks > 1 then
      plateBtn(P.upper(t("shop.fire")), 170, 96, function() S.cooks = S.cooks - 1; toast(t("ts.fired")); dirty = true end, 140, 24)
    end
  elseif id == "supplier" then
    text(t("sup.lead"), 10, 28, "tiny", brown, "left", 300)
    for k = 1, 3 do
      local y = 74 + (k - 1) * 40
      local sp = D.SUPPLIER[k]
      plateBtn(P.upper(t("sup." .. k)), 10, y, function() setSupplier(k) end, 130, 30, S.supplier == k)
      text(k == 1 and t("sup.d1") or t("sup.d", { q = sp.q, m = math.floor((sp.m - 1) * 100 + .5) }), 148, y + 2, "tiny", brown, "left", 162)
    end
  elseif id == "study" then
    text(t("study.lead"), 10, 28, "tiny", brown, "left", 300)
    local done = S.studyWeek == G.weekOf(S.day)
    plateBtn(done and P.upper(t("study.done")) or (P.upper(t("study.btn")) .. "  " .. P.eur(D.STUDY_COST)), 10, 76, runStudy, 200, 24)
    local y = 108
    for _, x in ipairs(S.tips) do
      for _, line in ipairs(G.tipText(x)) do
        if y > 210 then break end
        text("- " .. line, 10, y, "tiny", C.ink, "left", 300)
        local _, wr = fonts.tiny.f:getWrap("- " .. line, 300 / fonts.tiny.s)
        y = y + #wr * fonts.tiny.f:getHeight() * fonts.tiny.s + 2
      end
    end
  else
    plateBtn(P.upper(isArmed("reset") and t("ts.sure") or t("shop.reset")), 10, 40, resetGame, 300, 24, true)
  end
  langBtn()
end

drawBottom = function()
  hits = {}
  if report then drawReportBottom()
  elseif S.tab == "menu" then drawMenuBottom()
  elseif S.tab == "day" then drawDayBottom()
  elseif S.tab == "contest" then drawContestBottom()
  elseif S.tab == "shop" then drawShopBottom()
  else drawKitchenBottom() end
end
drawTopScreen = function()
  if report then drawReportTop()
  elseif S.tab == "menu" then drawMenuTop()
  elseif S.tab == "day" then drawDayTop()
  elseif S.tab == "contest" then drawContestTop()
  elseif S.tab == "shop" then drawShopTop()
  else drawTop() end
  drawToast()
end

-- ---------------------------------------------------------------- input
local drag = nil
local function benchPoint(x, y) return (x - PCX) / PR, (y - PCY) / PR end
local function touchDown(x, y)
  if renaming and not CONSOLE then finishRename(renameBuf) end   -- PC: a tap elsewhere keeps what was typed
  for k = #hits, 1, -1 do
    local h = hits[k]
    if x >= h.x and x < h.x + h.w and y >= h.y and y < h.y + h.h then h.fn(); return end
  end
  if S.tab ~= "kitchen" then return end
  for _, b in ipairs(BOWLS) do
    if x >= b.x - 6 and x <= b.x + BOWL_W + 6 and y - OY >= b.y - 4 and y - OY <= b.y + BOWL_H + 16 then setCut(b.g); return end
  end
  local px, py = benchPoint(x, y)
  if math.sqrt(px * px + py * py) > 1 then return end
  drag = { x = 9, y = 9 }
  if addPiece(px, py) then drag = { x = px, y = py } end
end
local function touchMove(x, y)
  if not drag then return end
  local px, py = benchPoint(x, y)
  if math.sqrt((px - drag.x) ^ 2 + (py - drag.y) ^ 2) > .2 and addPiece(px, py) then drag = { x = px, y = py } end
end
local function touchUp() drag = nil end

local held = {}
local function navButton(b)   -- outside the Kitchen: L/R and SELECT go through the screens, START quits
  if b == "leftshoulder" then goTab(-1)
  elseif b == "rightshoulder" or b == "back" then goTab(1)
  elseif b == "start" then save(); love.event.quit() end
end
local function otherButton(b)
  if report then if b == "a" then closeReport() end; return end
  if S.tab == "day" then
    if anim then
      if b == "a" then skipDay()
      elseif b == "dpleft" then anim.speed = math.max(1, anim.speed / 2)
      elseif b == "dpright" then anim.speed = math.min(4, anim.speed * 2) end
    elseif b == "a" then startDay() else navButton(b) end
  elseif S.tab == "contest" then
    if b == "dpup" then S.csel = math.max(1, S.csel - 1)
    elseif b == "dpdown" then S.csel = math.min(#S.menu, S.csel + 1)
    elseif b == "a" and S.menu[S.csel] then enterContest(S.menu[S.csel])
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
  if report or S.tab == "day" or S.tab == "contest" or S.tab == "shop" then otherButton(b); return end
  if S.tab == "menu" then menuButton(b); return end
  if b == "dpleft" then pickTopping(-1)
  elseif b == "dpright" then pickTopping(1)
  elseif b == "leftshoulder" then pickCat(-1)
  elseif b == "rightshoulder" then pickCat(1)
  elseif b == "dpup" then S.dough = cycle(D.DOUGH_ORDER, S.dough, 1); changed()
  elseif b == "dpdown" then S.sauce = cycle(D.SAUCE_ORDER, S.sauce, 1); changed()
  elseif b == "a" then setCut(1 - curCut())
  elseif b == "x" then rotatePiece()
  elseif b == "b" then undo()
  elseif b == "y" then clear()
  elseif b == "back" then goTab(1)
  elseif b == "start" then save(); love.event.quit() end
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
BOOT[#BOOT + 1] = { "fonts", function() fonts.tiny, fonts.small, fonts.body, fonts.big = mkFont(9), mkFont(11), mkFont(14), mkFont(26) end }
for i = 1, A.pages do
  BOOT[#BOOT + 1] = { "texture " .. i .. "/" .. A.pages, function() pages[i] = love.graphics.newImage("gfx/atlas" .. i .. ".png") end }
end
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
  love.graphics.print("Pizza Magna", 10, 10)
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
  if dirty then saveTimer = saveTimer + dt; if saveTimer > 1 then save(); saveTimer = 0 end end
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
