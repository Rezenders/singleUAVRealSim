////////////////Beliefs
waypoint(0,3,0,0.5).
waypoint(1,4,-1,0.5).
waypoint(2,2,1,0.5).
waypoint(3,2,1,5).
waypoint(4,0,0,0.5).
endOfTrip(5).

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
+!reachWP : sequenceCounter(S) & pos(X,Y,Z) & destination(Xd,Yd,Zd) & math.abs(X-Xd)<0.3 & math.abs(Y-Yd)<0.3 & math.abs(Z-Zd)<0.3
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
