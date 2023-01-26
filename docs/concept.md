# License Manager Concept

The License Manager (LM) is basically some Rest API. The LM API accepts and handles

* requests from authenticated users to buy (get) licenses
* requests from authenticated users to (implicitly) redeem a 
  license and get permissions to access some (connected) application

## Components

The LM works in some 'integrated' environment, which is made of

* an Application (APP) (in our case the 'bettermarks application'), where 
  users can do something
* a Hierarchy Provider (HP), which holds entity hierarchies (for more on hierarchies, see below). 
  HP is usually bundled with an Identity Provider (IDP)
* the License Manager (LM) itself.


![](diagrams/components.png)
Components of the 'license featured' application

## Entities and Hierarchies

We call users, school classes, schools, other organisational structures, even 
countries 'Entities' (E). Those entities can be arranged in some 'natural' hierarchy, 
f.e. some school has several classes, each of those classes has several students and 
one (or maybe more) teachers. An entity is uniquely identified within the HP by some 
identifier, we call it 'external identifier' (EID). 

The Hierarchy Provider (HP) stores those entities and their hierarchical relations.

## The Hierarchy Provider
The HP is also an API, where authenticated users
or other services as Clients can get information about hierarchies of specific
entities. In order to fulfill the requirements for some environment including an LM,
the following routes must be implemented by an HP:

### Getting Hierarchy Levels
```
GET /hierarchy/levels
```
This route returns the hierarchy levels, that are used in the specific
hierarchy structure of the domain. Those hierarchy levels are used to 
identify entities, which are associated with some given hierarchy level 
(see below). A call to the route returns something like
```json
{
    "student": 0, 
    "teacher": 0, 
    "class": 1, 
    "school": 2
}
```
There are two 'leaf levels' defined, 'teacher' and 'student' entity, a 'level 1' 
entity named 'class' and a 'level 2' entity named 'school'.

### Getting Hierarchies for a Specific User
```
GET /hierarchy/users/{user EID}
```
This route gets the hierarchy path(s) for a given user and returns something like
```json
[
    "school(999)/class(566)/teacher(glu::123)",
    "school(999)/class(344)/teacher(glu::123)",
    "school(888)/teacher(glu::123)"
]
```
This means that a user 'glu::123' (who is associated with a 'leaf'
hierarchy level 'teacher') is currently member of a hierarchy level 
named 'class' and has EID='344' and of some 'class' with EID='566', 
which both are 'located' in some hierarchy level 'school' with EID='999'.
Additionally, 'teacher' 'glu:123' is 'directly connected' to 'school' '888'.

## The License Manager
The LM is also some web service, that implements a couple of routes 
that can be used by the users of the application. The 'links' representing
the web service calls are provided to the users by the application. We are currently 
implementing a POC for such routes. We will implement the following routes:

### Getting Products
This route returns all 'available products'. For the POC, there is just one product, that is associated with
'full access'. Fine granular permissions within a product are not dealt with in the POC. But we already know, that
the place, where to define specific permissions (f.e. permissions to have access to specific books), is the
'product'.
```
GET /products
```
would return something like
```json
[
 {"eid": "full_access", "name": "Full access to bettermarks"} 
]
```

### Purchasing a license
The process of purchasing a license will be a multistep process (getting pricing information, add a license product 
with number of seats and duration to a 'shopping cart', purchase ...). We will not implement such a multistep process
in the POC, we will just add one route as follows:
```
POST /users/{user EID}/license/purchase
```
with some request body like
```json
{
  "product": "full_access"
  "level": "class"
  "entities": ["34535356324", "2346445645646"]
  "seats": 50
  "start": "2023-01-01"
  "end": "2023-12-31"
}
```
The request body will be interpreted like so: The requesting user wants to add (purchase) a
license for a product with EID='full_access' and an 'entity level' 'class'. He wants to 
buy the license to be valid from first of January 2023 to the last of December 2023. The
license should be valid for 50 'seats', that means, that 50 students (and/or teachers? TODO)
can use the license at the same time. The license should be valid for the students
(and teachers? TODO), that are members of classes with EID='34535356324' resp. 
EID='2346445645646". 

#### What happens when this route is being called:
Let us assume, the purchase function is called via
```
POST /users/1111111/license/purchase
```
using the request body given above.
The request handling function will first check,
* If the requesting user (given user_id), is loggend in and has issued the request. -> If not, return an error
* If the 'entities' in the request are ALL part of the users hierarchy. -> If not, return an error
  * In order to check this, zhe HP is called via ```GET /hierarchy/users/1111111```. 
    The result would be something like this:
    ```json
    [
      "school(999)/class(34535356324)/teacher(1111111)",
      "school(999)/class(34535356324)/teacher(1111111)",
      "school(888)/teacher(1111111)"
    ]
    ```
    We now apply a simple string search to the result list checking, if ALL entities in the request body have a
    match in the result list AND have correct 'level' (as given in the request body). -> If not, return an error!
    Yes, they have! So the license purchase request is valid in this case!
* The license will be stored in the database like so:
  Create a new row in the 'license' table:

  | product EID | purchaser	EID | owner level | owner EID	|
  |-------------|---------------|-------------|-------------|









##### TODO
for 'level 0' all entities (that is 'students'
and 'teachers', as we already know from having asked the HP about 'hierarchy levels'), that
have the given 'entities' in their 