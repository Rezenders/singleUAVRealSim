////////////////Beliefs
//waypoint(sequence,latitude,longitude, altitute relative to ground)
waypoint(0,-27.603683,-48.518052,10).
waypoint(1,-27.603815,-48.518572,10).
waypoint(2,-27.603815,-48.518572,20).
waypoint(3,-27.6040319,-48.518365,15).

endOfTrip(4).

!start.


////////////////Plans

//wait for a confirmation if all is set up
+!start : status(ready)
  <-  launch; //launch drone
      +sequenceCounter(0);
      +idle;
      !setCourse.
+!start
  <-  !start.

//set course to waypoint
+!setCourse : sequenceCounter(S) & waypoint(S, X, Y, Z) & idle & status(flying)
  <-  -idle;
      setWaypoint(X,Y,Z);//action set waypoint
      +destination(X,Y,Z);
      !reachWP.
+!setCourse : sequenceCounter(S) & waypoint(S, _, _, _)
  <-  !setCourse.
+!setCourse : endOfTrip(S) & sequenceCounter(S)
  <-  !land.
+!setCourse
  <-  .wait({+sequenceCounter(_)},1000,_);
      !setCourse.

//when wp is reached
+!reachWP : sequenceCounter(S) & pos(X,Y,Z) & destination(Xd,Yd,Zd) & math.abs(X-Xd)<1 & math.abs(Y-Yd)<1 & math.abs(Z-Zd)<1
  <-  -destination(Xd,Yd,Zd);
      -+sequenceCounter(S+1);
      +idle;
      !setCourse.
+!reachWP
  <-  .wait({+pos(_,_,_)},1000,_);
      !reachWP.
//-!reachWP

+!land : idle & sequenceCounter(S) & endOfTrip(S) & status(flying)
  <-  -idle;
      .print("LANDING");
      land. //land drone
+!land
  <-  !land.

+pos(X,Y,Z)
  <- .print("pos(", X, ", ", Y, ", ", Z, ")").
