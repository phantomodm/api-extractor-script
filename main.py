import bigcommerce
import pyrebase

bigConfig = {
    'client_id': '',
    'client_token': '',
    'store_hash': ''
}

fireBaseConfig = {
  "apiKey": "",
  "authDomain": "bc-firebase-db.firebaseapp.com",
  "databaseURL": "https://bc-firebase-db.firebaseio.com",
  "projectId": "bc-firebase-db",
  "storageBucket": "",
  "messagingSenderId": ""
}

# BC initialization
api = bigcommerce.api.BigcommerceApi(client_id=bigConfig["client_id"], store_hash=bigConfig["store_hash"],access_token=bigConfig["client_token"])
api_orders = api.Orders.all()

# Firebase initialization
firebase = pyrebase.initialize_app(fireBaseConfig)
fbRef = firebase.database()

extractedOrders = []

for order in api_orders:
    data = {}
    if order['status'] == "Shipped":
        data['orders'] = order
        order_details = api.Orders.get(int(order['id'])).products()
        for products in order_details:
            data['orders']['product_details'] = products['product_options']
            extractedOrders.append(data)
        print(len(extractedOrders))

for order in extractedOrders:
    apiOrders = order['orders']
    print('Adding order details')
    ordersRef = fbRef.child('bc_incoming_orders')
    orderRef = ordersRef.push({
        'bc_id': apiOrders.id,
        'date_created': apiOrders.date_created,
        'customer_id': apiOrders.customer_id,          
        'status': apiOrders.status,
        'total_ex_tax': apiOrders.total_ex_tax
    })
    print(apiOrders.id)

    fb_order_reference_key = orderRef['name']
    print(fb_order_reference_key)
    productOptionsKeyOrder = []

    for options in apiOrders['product_details']:
        orderDetails = fbRef.child('incoming_order_details')
        print('Adding product details per order')
        productOptionsKeyOrder.append(orderDetails.push({
            'option_name': options['display_name'],
            "option_value": options['display_value'],
            'order_id': fb_order_reference_key
        })['name'])

    print('Associating {} order to product details entries'.format(fb_order_reference_key))
    for orderKey in productOptionsKeyOrder:
        productsPerOrder = fbRef.child('productsPerOrder').child(orderRef['name']).child(orderKey)
        productsPerOrder.set(True)
