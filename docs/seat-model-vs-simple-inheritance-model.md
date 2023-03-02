# The Simple Inheritance License Model vs. the Seat License Model

In our 'licensing' scenario, we have some services, that can be separated from each other, but have
to 'communicate' with each other, either directly or using some 'indirect' way

## The Simple Inheritance License Model

The "simple inheritance license model" (SILM) is a license model that makes use of just
hierarchical entity structure. If an entity 'owns' a license, all the entities, that
'belong' to that entity (or are 'members' of that entity), directly or at some place in
the hierarchy path, also get the privileges that are associated with that license.

Example: A license for a school S with privilege 'access all' has been purchased. Class
C1 is 'member' of S. Teacher T1 and Student S1 are members of C1.
Privileges for both, the teacher T1 and the student S1 will be 'full access', as long as they are
members of C1. If student S1 leaves class C1, they will immediately lose the privileges, 
they got from S before.

## The Seat Model

The "seat model" (SM) also uses entity hierarchies, but in the seat model case,
a 'leaf entity', usually a user (teacher or student), will 'occupy' a 'seat', when some 
license is available for some owner entity, that is on a higher level in the leaf entities 
hierarchy path.

Example: Again, a license L for a school S with privilege 'access all' has been purchased. But now,
a 'number of seats' also is part of the license. And again, Class C1 is 'member' of S. Teacher T1 
and Student S1 are members of C1. If student S1 logs in for the first time, they will occupy a 
seat for license L. When student S1 leaves C1 again, the seat must be 'freed' again explicitly
by some mechanism.

## Comparing the Model
| -                                 | Simple Inheritance License Model                               | Seat Model                                                                                                                       |
|-----------------------------------|----------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|
| Purchasing                        | License has a 'product', an owner, valid from, valid to, and optionally some 'quota' | License has a 'product', an owner, valid from, valid to, and mandatory number of seats                                           |
| Redeeming                         | Redeeming is done implicitly                                   | Explicit redeeming by 'occupying' a seat for a license                                                                           |
| Privileges from multiple licenses | If a leaf entity 'matches' multiple licenses, they will get privileges from ALL 'matched' licenses | Redeeming seats for additional licenses is a not yet defined and maybe complicated process.                                      |
| 'Freeing' seats | Happens implicitly. If a leaf entity is no longer in the 'hierarchy path' of an owner entity, the leaf entity no longer has access to the licnese owned by the owner entity | Seats must be 'released' explicitly. Process for releasing is not yet defined and is maybe complicated.                          |
 | Getting Permissions | just a 'union' of all permissions from all licenses that match | Complicated in case of multiple license, multiple privilege case. Getting 'unions' is hard.                                      |
| Performance | Using methods like 'materialized views' in the DB, asking for privileges of an entity is FAST | We have to query for already occupied seats as well as for 'seats to redeem', performance is still good, but not as good as SILM |

## Conclusion

The SILM model is much more simple than SA. It is easy to implement and it is very robust. 
The main drawback of the SILM model is, that you do not have control over 'occupied' seats.
Furthermore, hte implicit occupation of 'seats' in the SILM model is 'greedy'. That means, even, if
2 licenses, that would match for a leaf entity would give the same privileges, BOTH licenses
would be occupied implicitly by the SILM model.
