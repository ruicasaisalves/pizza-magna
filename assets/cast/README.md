# Pizza Magna character pilot

The pack contains 21 customer looks, four waiters and five stationary cooks. Extract the ZIP and open preview.html in a browser to inspect the exported art. The game-facing identifiers are zero based. Folder 01 maps to look 0 and folder 21 maps to look 20.

## Customers

Each customers/NN/walk.png has five columns and four rows of 32 × 58. Use column 0 for idle and columns 1–4 for successive walking steps. Rows face down, right, up and left. Anchor the sprite at rounded x and rounded y + T − 58. Sort by y + T. The left-facing views of the new walking sheets mirror the corresponding right-facing views.

Each customers/NN/seated.png is a single column of four 32 × 48 cells in the same direction order. Offset each seated customer using the seat position and depth in the existing room layout. Chairs, tables, plates and pizzas have their own room layers. For customers 08–14 the package includes the chair-height correction.

## Waiters and cooks

Each waiters/NN/service.png has 32 × 58 cells. For each of the four directions there is an empty row followed by a carrying row. Use column 0 at rest, columns 1–4 in motion and column 5 for the delivery. At delivery show the empty row in the direction of the customer's seat for the existing 0.3 seconds of game time. The plate is part of the carrying sprite.

Each cooks/NN/idle.png is one front-facing 32 × 58 frame. Draw it at that cook's position with the same foot anchor as the customers.

## Handoff

Start a fresh branch from updated main. Load the new sheets behind PM_DEV after image decode and fall back to the shipped atlas while loading. Test normal and fast service, depth sorting, four directions at the table and the mobile room. The restaurant captures supplied with the download show a staged local scene. PR and merge require Rui's explicit instruction.
