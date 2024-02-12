(define (domain merged_domain)
    (:requirements :conditional-effects :typing)
    (:types
        camera lander mode objective othergoals rover store waypoint
    )
    (:predicates
        (at ?x - rover ?y - waypoint)
        (atlander ?x - lander ?y - waypoint)
        (cantraverse ?r - rover ?x - waypoint ?y - waypoint)
        (equippedforsoilanalysis ?r - rover)
        (equippedforrockanalysis ?r - rover)
        (equippedforimaging ?r - rover)
        (empty ?s - store)
        (haverockanalysis ?r - rover ?w - waypoint)
        (havesoilanalysis ?r - rover ?w - waypoint)
        (full ?s - store)
        (calibrated ?c - camera ?r - rover)
        (supports ?c - camera ?m - mode)
        (available ?r - rover)
        (visible ?w - waypoint ?p - waypoint)
        (haveimage ?r - rover ?o - objective ?m - mode)
        (communicatedsoildata ?w - waypoint)
        (communicatedrockdata ?w - waypoint)
        (communicatedimagedata ?o - objective ?m - mode)
        (atsoilsample ?w - waypoint)
        (atrocksample ?w - waypoint)
        (visiblefrom ?o - objective ?w - waypoint)
        (storeof ?s - store ?r - rover)
        (calibrationtarget ?i - camera ?o - objective)
        (onboard ?i - camera ?r - rover)
        (channelfree ?l - lander)
        (robot_failed)

    )

    (:action navigate
:parameters (?x - rover ?y - waypoint ?z - waypoint)
:precondition
(and
( at ?x ?y )
( visible ?y ?z )
( cantraverse ?x ?y ?z )
( available ?x )

)
:effect
(and
( at ?x ?z )
(not ( at ?x ?y ))
)
)

(:action samplesoil
:parameters (?x - rover ?s - store ?p - waypoint)
:precondition
(and
( at ?x ?p )
( atsoilsample ?p )
( empty ?s )
( equippedforsoilanalysis ?x )
( storeof ?s ?x )

)
:effect
(and
( havesoilanalysis ?x ?p )
( full ?s )
(not ( empty ?s ))
(not ( atsoilsample ?p ))
)
)

(:action samplerock
:parameters (?x - rover ?s - store ?p - waypoint)
:precondition
(and
( atrocksample ?p )
( at ?x ?p )
( equippedforrockanalysis ?x )
( empty ?s )
( storeof ?s ?x )

)
:effect
(and
( full ?s )
( haverockanalysis ?x ?p )
(not ( empty ?s ))
(not ( atrocksample ?p ))
)
)

(:action communicatesoildata
:parameters (?r - rover ?l - lander ?p - waypoint ?x - waypoint ?y - waypoint)
:precondition
(and
( havesoilanalysis ?r ?p )
( available ?r )
( visible ?x ?y )
( at ?r ?x )
( atlander ?l ?y )
( channelfree ?l )

)
:effect
(and
( available ?r )
( communicatedsoildata ?p )
( channelfree ?l )

)
)

(:action communicaterockdata
:parameters (?r - rover ?l - lander ?p - waypoint ?x - waypoint ?y - waypoint)
:precondition
(and
( channelfree ?l )
( at ?r ?x )
( haverockanalysis ?r ?p )
( available ?r )
( visible ?x ?y )
( atlander ?l ?y )

)
:effect
(and
( available ?r )
( channelfree ?l )
( communicatedrockdata ?p )

)
)

(:action communicateimagedata
:parameters (?r - rover ?l - lander ?o - objective ?m - mode ?x - waypoint ?y - waypoint)
:precondition
(and
( haveimage ?r ?o ?m )
( visible ?x ?y )
( channelfree ?l )
( atlander ?l ?y )
( at ?r ?x )
( available ?r )

)
:effect
(and
( channelfree ?l )
( communicatedimagedata ?o ?m )
( available ?r )

)
)

(:action takeimage
:parameters (?r - rover ?p - waypoint ?o - objective ?i - camera ?m - mode)
:precondition
(and
( visiblefrom ?o ?p )
( calibrated ?i ?r )
( supports ?i ?m )
( at ?r ?p )
( onboard ?i ?r )

)
:effect
(and
( haveimage ?r ?o ?m )
(not ( calibrated ?i ?r ))
)
)

(:action calibrate
:parameters (?r - rover ?i - camera ?t - objective ?w - waypoint)
:precondition
(and
( onboard ?i ?r )
( at ?r ?w )
( calibrationtarget ?i ?t )

)
:effect
(and
( calibrated ?i ?r )

)
)

(:action drop
:parameters (?x - rover ?y - store)
:precondition
(and
( full ?y )

)
:effect
(and
( empty ?y )
(not ( full ?y ))
)
)


)