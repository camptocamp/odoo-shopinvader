Currently, sale.order:_update_programs_and_rewards() is called only when strictly needed (when no reward line exists), and of course only if not locked order.
It would be a good addition to add a new POST route in the module to explicitly call ``sale.order:_update_programs_and_rewards()``
