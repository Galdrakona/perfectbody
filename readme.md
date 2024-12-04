# PerfectBody project

Online store with admin panel.

## Database

- [ ] user_profile
  - [ ] id
  - [ ] account_type
  - [ ] role
  - [ ] login
  - [ ] password
  - [ ] avatar
  - [ ] first_name
  - [ ] last_name
  - [ ] phone_number
  - [ ] email
  - [ ] preferred_communication_channel
  - [ ] user_creation_datetime
- [ ] address
  - [ ] id
  - [ ] user_id (1:n -> user)
  - [ ] address_type
  - [ ] street
  - [ ] town
  - [ ] postal_code
  - [ ] country
- [ ] product
  - [ ] id
  - [ ] product_type
  - [ ] product_name
  - [ ] product_description
  - [ ] product_view
  - [ ] category_id (1:n -> category)
  - [ ] price
  - [ ] producer_id (1:n -> producer)
  - [ ] stock_availability
- [ ] category
  - [ ] id
  - [ ] category_name
  - [ ] category_description
  - [ ] category_parent_id (1:n -> category)
- [ ] trainers_services
  - [ ] id
  - [ ] description
  - [ ] trainers (n:m -> user)
  - [ ] services (n:m -> product)
- [ ] order
  - [ ] id
  - [ ] user_id (1:n -> user)
  - [ ] order_state
  - [ ] order_creation_datetime
  - [ ] total_price
  - [ ] billing_address_id (1:n -> address)
  - [ ] shipping_address_id (1:n -> address)
- [ ] orders_products
  - [ ] id
  - [ ] orders (n:m -> order)
  - [ ] product_id (1:n -> product)
  - [ ] quantity
  - [ ] price_per_item
- [ ] producer
  - [ ] id
  - [ ] producer_name
- [ ] product_review
  - [ ] id
  - [ ] product_id (1:n -> product)
  - [ ] reviewer_id (1:n -> user)
  - [ ] rating
  - [ ] comment
  - [ ] review_creation_datetime
- [ ] trainer_review
  - [ ] id
  - [ ] trainer_id (1:n -> user)
  - [ ] reviewer_id (1:n -> user)
  - [ ] rating
  - [ ] comment
  - [ ] review_creation_datetime