This allows to manage multiple carts per user.

It exposes a new service `carts` to fetch the user's stored carts, read them,
delete them, or select any of them as the current cart.

It also adds a new method `store` on the `cart` service, to stash the current
cart. It can later be accessed and eventually restored from the `carts` service.

Stored carts are identified with the typology `stored`.
