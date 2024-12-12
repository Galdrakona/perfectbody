# PerfectBody project

Online store with admin panel.

## Functionalities

- [x] products/services list (products-list)
- [ ] product/service information (product-detail)

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
- [x] product
  - [x] id
  - [x] product_type
  - [x] product_name
  - [x] product_description
  - [x] product_view
  - [x] category_id (1:n -> category)
  - [x] price
  - [x] producer_id (1:n -> producer)
  - [x] stock_availability
- [x] category
  - [x] id
  - [x] category_name
  - [x] category_description
  - [ ] category_view
  - [x] category_parent_id (1:n -> category)
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
- [x] producer
  - [x] id
  - [x] producer_name
- [ ] product_review
  - [ ] id
  - [ ] product_id (1:n -> product)
  - [ ] reviewer_id (1:n -> user)
  - [ ] rating
  - [ ] comment
  - [ ] review_creation_datetime
  - [ ] review_update_datetime
- [ ] trainer_review
  - [ ] id
  - [ ] trainer_id (1:n -> user)
  - [ ] reviewer_id (1:n -> user)
  - [ ] rating
  - [ ] comment
  - [ ] review_creation_datetime
  - [ ] review_update_datetime