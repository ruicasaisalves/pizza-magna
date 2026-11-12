-- On the 3DS the screens are fixed (top 400x240, bottom 320x240). On a PC the window shows both,
-- one above the other, so the port can be tried without a console.
function love.conf(t)
  t.identity = "pizzamagna"
  t.window.title = "Pizza Magna 3DS"
  t.window.width = 400
  t.window.height = 480
  t.window.stencil = true
  t.modules.physics = false
end
