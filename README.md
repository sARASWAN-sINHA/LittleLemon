# LittleLemon
A fully functioning API project for a restaurant so that the client application developers can use the APIs to develop web and mobile applications. People with different roles will be able to browse, add and edit menu items, place orders, browse orders, assign delivery crew to orders and finally deliver the orders.

# User groups
Create the following two user groups and then create some random users and assign them to these groups from the Django admin panel. 

 - Manager

- Delivery crew

Users not assigned to a group will be considered Customers. 

# HTTP Status code

200- Ok &nbsp;  &nbsp;   &nbsp; For all successful GET, PUT, PATCH and DELETE calls

201 - Created &nbsp;  &nbsp;   &nbsp;           For all successful POST requests

403 - Unauthorized &nbsp;  &nbsp;   &nbsp;       If authorization fails for the current user token

401 – Forbidden &nbsp;  &nbsp;   &nbsp;          If user authentication fails

400 – Bad request &nbsp;  &nbsp;   &nbsp;        If validation fails for POST, PUT, PATCH and DELETE calls

404 – Not found &nbsp;  &nbsp;   &nbsp;          If the request was made for a non-existing resource


# API endpoints 
Here are all the required API routes for this project grouped into several categories.


![image](https://user-images.githubusercontent.com/59411538/235428115-6df3cd1b-557c-4f7a-bc97-4ae02b028df9.png)
![image](https://user-images.githubusercontent.com/59411538/235428172-d71df044-6fe1-4247-8fb0-807e712f94a3.png)
![image](https://user-images.githubusercontent.com/59411538/235428278-1544f629-c4e2-4ef8-9e67-6a4f9029cb34.png)
![image](https://user-images.githubusercontent.com/59411538/235428334-3af98b26-7b6e-4f6e-904b-8920a97badbc.png)
![image](https://user-images.githubusercontent.com/59411538/235428375-5ad2572a-f298-4102-b3c4-dc569c1c8eff.png)


## Note: Some extra 1 or 2 APIs are also added which may not be shown above. Please refer to thr postman collection json added to the respository.
--Please feel free to add some more APIs or update them as you need

