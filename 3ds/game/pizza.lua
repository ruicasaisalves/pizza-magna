--[[ The pizza rules, ported from index.html (PIZZA ANALYSIS and the kitchen helpers). Data comes from data.lua
     (generated from index.html by tools/export_3ds.js); the logic here must follow analyze(), portion() and
     packPieces() by hand when they change. Lua 5.1: no bit operators, no goto, no utf8 library. ]]
local D = require("data")
local A = require("atlas")
local P = {}
local unpack = unpack or table.unpack
P.D, P.A = D, A

local LANG = "en"
function P.setLang(l) LANG = (l == "pt") and "pt" or "en" end
function P.lang() return LANG end

-- text from the I18N table, with {x}-style values
function P.t(key, vars)
  local s = (D.I18N[LANG] and D.I18N[LANG][key]) or D.I18N.en[key] or key
  if vars then s = s:gsub("{(%w+)}", function(k) local v = vars[k]; return v ~= nil and tostring(v) or "{" .. k .. "}" end) end
  return s
end
local t = P.t

local function round(v) return math.floor(v + .5) end
local function clamp(v, a, b) return math.max(a, math.min(b, v)) end
local function r2(v) return round(v * 100) / 100 end
P.round, P.clamp = round, clamp

function P.eur(v)
  local s = string.format("%.2f", math.abs(r2(v)))
  return (v < 0 and "-" or "") .. "$" .. s
end
function P.fmtG(g)
  if g >= 1000 then
    local s = string.format("%.2f", g / 1000)
    if LANG == "pt" then s = s:gsub("%.", ",") end
    return s .. " kg"
  end
  return g .. " g"
end

-- capital letters, Portuguese accents included (string.upper leaves them as they are)
local UP = { ["á"]="Á",["à"]="À",["â"]="Â",["ã"]="Ã",["ç"]="Ç",["é"]="É",["ê"]="Ê",["í"]="Í",["ó"]="Ó",["ô"]="Ô",["õ"]="Õ",["ú"]="Ú",["ü"]="Ü",["ñ"]="Ñ" }
function P.upper(s) return (s:upper():gsub("[\195][\128-\191]", function(c) return UP[c] or c end)) end
-- a sort key without accents, so Ananás sorts among the A's
local FOLD = { ["á"]="a",["à"]="a",["â"]="a",["ã"]="a",["ç"]="c",["é"]="e",["ê"]="e",["í"]="i",["ó"]="o",["ô"]="o",["õ"]="o",["ú"]="u",["ü"]="u",["ñ"]="n" }
function P.fold(s) return (s:lower():gsub("[\195][\128-\191]", function(c) return FOLD[c] or c end)) end

local function set(list) local s = {}; for _, v in ipairs(list) do s[v] = true end; return s end
local CASA, EXOTIC, BIG_SHRED, CENTRED = set(D.CASA), set(D.EXOTIC), set(D.BIG_SHRED), set(D.CENTRED)
P.BIG_SHRED, P.CENTRED = BIG_SHRED, CENTRED
local function has(list, v) for _, x in ipairs(list) do if x == v then return true end end; return false end
P.has = has

function P.ingName(id) return t("ing." .. id) end
function P.ingC(id) return D.ING[id].c end   -- supplier 1 (the prototype has no shop yet)

-- sprites and turning pieces (see turned() in index.html; the export already holds the four turns)
local F = A.frames
function P.frame(key) return F[key] end
function P.canGrate(id) return F[id .. "_g0"] ~= nil end
function P.turns(id) return F[id .. "_q0"] and (D.ING[id].rot or 1) or 1 end
function P.canRotate(id) return P.turns(id) > 1 end
local function pieceVar(x) return (x.v ~= nil and x.v or math.floor(x.r * 7)) % 3 end
local function pieceAng(x) return (x.a ~= nil and x.a or pieceVar(x)) % P.turns(x.i) end
function P.wholeKey(id, v, a) if F[id .. "_q0"] then return id .. "_q" .. (a % P.turns(id)) end; return id .. "_" .. v end
function P.pieceKey(x)
  if x.g and P.canGrate(x.i) then return x.i .. "_g" .. pieceVar(x) end
  return P.wholeKey(x.i, pieceVar(x), pieceAng(x))
end

-- weights and portions (portion(), pieceGrams() in index.html)
function P.portion(x)
  if x.g then return BIG_SHRED[x.i] and D.SHRED_W or D.GRATED_W end
  return D.WHOLE_W[x.i] or 1
end
function P.pieceGrams(x) return ((x.g and D.GRAMS_GRATED[x.i]) or D.GRAMS[x.i] or 10) * P.portion(x) end
function P.pizzaGrams(p) local g = 0; for _, x in ipairs(p.pieces) do g = g + P.pieceGrams(x) end; return round(g) end

local function isCheese(id) return has(D.ING[id].t, "queijo") end
P.isCheese = isCheese
function P.ingCat(id)
  if has(D.HERBS, id) then return "ervas" end
  if has(D.EXTRAS, id) then return "extras" end
  for _, c in ipairs({ "queijo", "carne", "peixe", "doce", "vegetal" }) do if has(D.ING[id].t, c) then return c end end
  return "extras"
end
-- why a topping has no chopped form (noCutKind)
function P.noCutKind(id)
  if has({ "nutella", "maionese", "natas_azedas", "catupiry" }, id) then return "spread" end
  if has({ "milho", "pinhoes", "batata_palha", "grao" }, id) then return "small" end
  return "drizzle"
end

local baseCost = D.DOUGHS.fina.c + D.SAUCES.tomate.c
function P.suggestPrice(cost) return math.max(3, r2(D.BASE_PRICE + (cost - baseCost) * D.MARKUP)) end

local DOUGH_Q = { fina = 3, napo = 5, alta = 2, integral = 3, sem_gluten = 1, lenta = 7, recheado = 3 }
local SAUCE_Q = { tomate = 5, natas = 2, pesto = 4, barbecue = 3, arrabbiata = 5, azeite_alho = 3, trufa = 6, pimentos = 4 }

-- analyze() from index.html: quality, cost, appeal per customer group, notes and combos
function P.analyze(p)
  local cnt, ids, n, cost0, grated = {}, {}, 0, 0, 0
  for _, x in ipairs(p.pieces) do
    if not cnt[x.i] then cnt[x.i] = 0; ids[#ids + 1] = x.i end
    cnt[x.i] = cnt[x.i] + 1
    local w = P.portion(x); n = n + w; cost0 = cost0 + P.ingC(x.i) * w
    if x.g then grated = grated + 1 end
  end
  n = round(n * 10) / 10
  local d = #ids
  local Dg, S, notes = D.DOUGHS[p.dough], D.SAUCES[p.sauce], {}
  local function note(kind, k) notes[#notes + 1] = { kind, t("n." .. k) } end
  local q = 45 + DOUGH_Q[p.dough]
  if p.sauce == "sem" then q = q - 12; note("bad", "dry") else q = q + SAUCE_Q[p.sauce] end
  if n < 6 then q = q - 25; note("bad", "empty")
  elseif n < 14 then q = q - (14 - n) * 1.5; note("bad", "few")
  elseif n > 150 then q = q - (n - 150) * .8; note("bad", "heavy")
  else note("good", "good") end
  if n > 0 then
    local cheese = false
    for _, i in ipairs(ids) do if isCheese(i) then cheese = true end end
    if not cheese then q = q - 10; note("bad", "nocheese") end
  end
  if d == 1 then q = q - 5; note("bad", "mono") end
  q = q + math.min(d, 5) * 2
  if #p.pieces >= 8 then
    local qd = { 0, 0, 0, 0 }
    for _, x in ipairs(p.pieces) do
      local k = 1 + (x.x >= 0 and 1 or 0) + (x.y >= 0 and 2 or 0)
      qd[k] = qd[k] + (x.g and 1.4 or 1)
    end
    local ratio = math.min(unpack(qd)) / math.max(unpack(qd))
    q = q - (1 - ratio) * 14
    if ratio < .4 then note("bad", "uneven") elseif grated >= 4 and ratio >= .7 then note("good", "grated") end
  end
  local function hasReq(k)
    if k:sub(1, 2) == "s:" then return p.sauce == k:sub(3) end
    return (cnt[k] or 0) >= 2
  end
  local combos, segMod = {}, { estudante = 0, familia = 0, turista = 0, gourmet = 0 }
  for _, c in ipairs(D.COMBOS) do
    local ok = true
    for _, r in ipairs(c.req) do if not hasReq(r) then ok = false; break end end
    if ok then
      combos[#combos + 1] = c.id
      q = q + c.q
      for k, v in pairs(c.seg) do segMod[k] = segMod[k] + v end
      local nm = t("combo." .. c.id)
      notes[#notes + 1] = c.q >= 0 and { "combo", t("n.combo", { x = nm }) } or { "bad", t("n.clash", { x = nm }) }
    end
  end
  q = clamp(round(q), 0, 100)
  local cost = Dg.c + S.c + cost0
  local tags = {}
  local function add(list) for _, tg in ipairs(list) do tags[#tags + 1] = tg end end
  for _, i in ipairs(ids) do
    add(D.ING[i].t)
    if CASA[i] then tags[#tags + 1] = "casa" end
    if EXOTIC[i] then tags[#tags + 1] = "exotico" end
  end
  add(S.t); add(Dg.t)
  local appeal = {}
  for _, k in ipairs(D.SEG_ORDER) do
    local sg, tw = D.SEG[k], 0
    for _, tg in ipairs(tags) do tw = tw + (sg.w[tg] or 0) end
    tw = clamp(tw, -20, 18)
    local a = q + tw + sg.dough[p.dough] + segMod[k]
    if k == "gourmet" and n > 34 then a = a - 8 end
    if k == "estudante" and n >= 24 then a = a + 3 end
    appeal[k] = clamp(round(a), 0, 100)
  end
  return { q = q, cost = r2(cost), appeal = appeal, notes = notes, combos = combos, n = n, d = d }
end

-- quality colour on a dark background (qColor(q,true)): red up to 25, yellow around 55, green from 85
function P.qColor(q)
  local h = clamp((q - 25) / 60, 0, 1) * 120 / 360
  local s, l = .9, .62
  local function hue(p, qq, tt)
    if tt < 0 then tt = tt + 1 end; if tt > 1 then tt = tt - 1 end
    if tt < 1 / 6 then return p + (qq - p) * 6 * tt end
    if tt < 1 / 2 then return qq end
    if tt < 2 / 3 then return p + (qq - p) * (2 / 3 - tt) * 6 end
    return p
  end
  local qq = l < .5 and l * (1 + s) or l + s - l * s
  local pp = 2 * l - qq
  return { hue(pp, qq, h + 1 / 3), hue(pp, qq, h), hue(pp, qq, h - 1 / 3) }
end

--[[ Compact pieces, the same format as saves, recipe links (#p=) and .pizza files in the browser game:
     "id1,id2|<base64url>", 5 bytes a piece (ingredient index, x, y, random turn, flags). ]]
local B64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
local function b64enc(bytes)
  local out = {}
  for k = 1, #bytes, 3 do
    local a, b, c = bytes[k], bytes[k + 1], bytes[k + 2]
    local v = a * 65536 + (b or 0) * 256 + (c or 0)
    local n = b == nil and 2 or (c == nil and 3 or 4)
    for j = 1, n do
      local s = math.floor(v / 2 ^ (6 * (4 - j))) % 64
      out[#out + 1] = B64:sub(s + 1, s + 1)
    end
  end
  return table.concat(out)
end
local function b64dec(s)
  local val, bytes, acc, bits = {}, {}, 0, 0
  for k = 1, #B64 do val[B64:sub(k, k)] = k - 1 end
  for k = 1, #s do
    local v = val[s:sub(k, k)]
    if v then
      acc = acc * 64 + v; bits = bits + 6
      if bits >= 8 then
        bits = bits - 8
        local byte = math.floor(acc / 2 ^ bits)
        bytes[#bytes + 1] = byte
        acc = acc - byte * 2 ^ bits
      end
    end
  end
  return bytes
end
function P.packPieces(ps)
  local ids, idx, u = {}, {}, {}
  for _, x in ipairs(ps) do if not idx[x.i] then ids[#ids + 1] = x.i; idx[x.i] = #ids - 1 end end
  local function qv(v) return math.max(0, math.min(255, round((v + 1) * 127.5))) end
  for _, x in ipairs(ps) do
    local fl = (x.v or 0) % 4 + (x.g and 4 or 0) + (x.a ~= nil and (8 + (x.a % 4) * 16) or 0)
    u[#u + 1] = idx[x.i]; u[#u + 1] = qv(x.x); u[#u + 1] = qv(x.y)
    u[#u + 1] = round(((x.r or 0) % 6.2832) / 6.2832 * 255); u[#u + 1] = fl
  end
  return table.concat(ids, ",") .. "|" .. b64enc(u)
end
-- toFixed(n) as a number, like the browser, so a pizza packed again gives the same bytes
local function fixed(v, n) local m = 10 ^ n; return (v < 0 and -1 or 1) * math.floor(math.abs(v) * m + .5) / m end
function P.unpackPieces(str)
  local idsS, b = str:match("^([^|]*)|(.*)$")
  local out = {}
  if not idsS then return out end
  local idl = {}
  for id in idsS:gmatch("[^,]+") do idl[#idl + 1] = id end
  local u = b64dec(b)
  for k = 1, #u - 4, 5 do
    local i = idl[u[k] + 1]
    if i and D.ING[i] then
      local fl = u[k + 4]
      local x = { i = i, x = fixed(u[k + 1] / 127.5 - 1, 3), y = fixed(u[k + 2] / 127.5 - 1, 3), r = fixed(u[k + 3] / 255 * 6.2832, 2), v = math.min(2, fl % 4) }
      if math.floor(fl / 4) % 2 == 1 then x.g = 1 end
      if math.floor(fl / 8) % 2 == 1 then x.a = math.floor(fl / 16) % 4 end
      if math.sqrt(x.x * x.x + x.y * x.y) <= .82 then out[#out + 1] = x end
    end
  end
  return out
end

return P
