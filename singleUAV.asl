////////////////Beliefs
//waypoint(sequence,latitude,longitude, altitute relative to ground)
waypoint(0,-27.603683,-48.518052,10).
waypoint(1,-27.603815,-48.518572,10).
//waypoint(2,-27.603815,-48.518572,20).
//waypoint(3,-27.6040319,-48.518365,15).

//end_of_trip(4).

!start.


////////////////Plans

//wait for a confirmation if all is set up
+!start : status(ready) & .my_name(N)
  <-  launch; //launch drone
      +sequence_counter(0);
      +idle;
      !set_course.
+!start
  <-  !start.

//set course to waypoint
+!set_course : sequence_counter(S) & waypoint(S, Xw, Yw, Zw) & idle & status(flying)
  <-  -idle;
      setWaypoint(Xw,Yw,Zw);//action set waypoint
      +destination(Xw,Yw,Zw);
      !reach_wp.
+!set_course : sequence_counter(S) & waypoint(S, _, _, _)
  <-  !set_course.
+!set_course : end_of_trip(S) & sequence_counter(S)
  <-  !land.
+!set_course
  <-  .wait({+sequence_counter(_)},1000,_);
      !set_course.

//when wp is reached
+!reach_wp : sequence_counter(S) & pos(X,Y,Z) & destination(Xd,Yd,Zd) & jia.gps_dist(X,Y,Z,Xd,Yd,Zd,D) & D<6
  <-
      -destination(Xd,Yd,Zd);
      -+sequence_counter(S+1);
      +idle;
      !set_course.
+!reach_wp
  <-  .wait({+pos(_,_,_)},1000,_);
      !reach_wp.

//-!reach_wp

+!land : idle & sequence_counter(S) & end_of_trip(S) & status(flying)
  <-  -idle;
      .print("LANDING");
      land. //land drone
+!land
  <-  !land.

+pos(X,Y,Z)
  <- .print("pos(", X, ", ", Y, ", ", Z, ")").
