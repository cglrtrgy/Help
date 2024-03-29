(define (domain merged_domain)
    (:requirements :conditional-effects :typing)
    (:types camera lander mode objective othergoals rover store waypoint)
    (:predicates (at ?x - rover ?y - waypoint)  (atlander ?x - lander ?y - waypoint)  (atrocksample ?w - waypoint)  (atsoilsample ?w - waypoint)  (available ?r - rover)  (calibrated ?c - camera ?r - rover)  (calibrationtarget ?i - camera ?o - objective)  (cantraverse ?r - rover ?x - waypoint ?y - waypoint)  (channelfree ?l - lander)  (communicatedimagedata ?o - objective ?m - mode)  (communicatedrockdata ?w - waypoint)  (communicatedsoildata ?w - waypoint)  (empty ?s - store)  (equippedforimaging ?r - rover)  (equippedforrockanalysis ?r - rover)  (equippedforsoilanalysis ?r - rover)  (full ?s - store)  (haveimage ?r - rover ?o - objective ?m - mode)  (haverockanalysis ?r - rover ?w - waypoint)  (havesoilanalysis ?r - rover ?w - waypoint)  (onboard ?i - camera ?r - rover)  (r_at ?x - rover ?y - waypoint)  (r_atlander ?x - lander ?y - waypoint)  (r_atrocksample ?w - waypoint)  (r_atsoilsample ?w - waypoint)  (r_available ?r - rover)  (r_calibrated ?c - camera ?r - rover)  (r_calibrationtarget ?i - camera ?o - objective)  (r_cantraverse ?r - rover ?x - waypoint ?y - waypoint)  (r_channelfree ?l - lander)  (r_communicatedimagedata ?o - objective ?m - mode)  (r_communicatedrockdata ?w - waypoint)  (r_communicatedsoildata ?w - waypoint)  (r_empty ?s - store)  (r_equippedforimaging ?r - rover)  (r_equippedforrockanalysis ?r - rover)  (r_equippedforsoilanalysis ?r - rover)  (r_full ?s - store)  (r_haveimage ?r - rover ?o - objective ?m - mode)  (r_haverockanalysis ?r - rover ?w - waypoint)  (r_havesoilanalysis ?r - rover ?w - waypoint)  (r_onboard ?i - camera ?r - rover)  (r_storeof ?s - store ?r - rover)  (r_supports ?c - camera ?m - mode)  (r_visible ?w - waypoint ?p - waypoint)  (r_visiblefrom ?o - objective ?w - waypoint)  (robot_failed) (storeof ?s - store ?r - rover)  (supports ?c - camera ?m - mode)  (visible ?w - waypoint ?p - waypoint)  (visiblefrom ?o - objective ?w - waypoint))
    (:action calibrate
        :parameters (?r - rover ?i - camera ?t - objective ?w - waypoint )
        :precondition (and (onboard ?i ?r) (at ?r ?w) (calibrationtarget ?i ?t))
        :effect (and (calibrated ?i ?r) (when (not (and (r_equippedforimaging ?r) (r_calibrationtarget ?i ?t) (r_at ?r ?w) (r_visiblefrom ?t ?w) (r_onboard ?i ?r))) (robot_failed)) (when (and (r_equippedforimaging ?r) (r_calibrationtarget ?i ?t) (r_at ?r ?w) (r_visiblefrom ?t ?w) (r_onboard ?i ?r) (not (robot_failed))) (and (r_calibrated ?i ?r))))
    )
     (:action communicateimagedata
        :parameters (?r - rover ?l - lander ?o - objective ?m - mode ?x - waypoint ?y - waypoint )
        :precondition (and (haveimage ?r ?o ?m) (visible ?x ?y) (channelfree ?l) (atlander ?l ?y) (at ?r ?x) (available ?r))
        :effect (and (channelfree ?l) (communicatedimagedata ?o ?m) (available ?r) (when (not (and (r_at ?r ?x) (r_atlander ?l ?y) (r_haveimage ?r ?o ?m) (r_visible ?x ?y) (r_available ?r) (r_channelfree ?l))) (robot_failed)) (when (and (r_at ?r ?x) (r_atlander ?l ?y) (r_haveimage ?r ?o ?m) (r_visible ?x ?y) (r_available ?r) (r_channelfree ?l) (not (robot_failed))) (and (not (r_available ?r)) (not (r_channelfree ?l)) (r_channelfree ?l) (r_communicatedimagedata ?o ?m) (r_available ?r))))
    )
     (:action communicaterockdata
        :parameters (?r - rover ?l - lander ?p - waypoint ?x - waypoint ?y - waypoint )
        :precondition (and (channelfree ?l) (at ?r ?x) (haverockanalysis ?r ?p) (available ?r) (visible ?x ?y) (atlander ?l ?y))
        :effect (and (available ?r) (channelfree ?l) (communicatedrockdata ?p) (when (not (and (r_at ?r ?x) (r_atlander ?l ?y) (r_haverockanalysis ?r ?p) (r_visible ?x ?y) (r_available ?r) (r_channelfree ?l))) (robot_failed)) (when (and (r_at ?r ?x) (r_atlander ?l ?y) (r_haverockanalysis ?r ?p) (r_visible ?x ?y) (r_available ?r) (r_channelfree ?l) (not (robot_failed))) (and (not (r_available ?r)) (not (r_channelfree ?l)) (r_channelfree ?l) (r_communicatedrockdata ?p) (r_available ?r))))
    )
     (:action communicatesoildata
        :parameters (?r - rover ?l - lander ?p - waypoint ?x - waypoint ?y - waypoint )
        :precondition (and (havesoilanalysis ?r ?p) (available ?r) (visible ?x ?y) (at ?r ?x) (atlander ?l ?y) (channelfree ?l))
        :effect (and (available ?r) (communicatedsoildata ?p) (channelfree ?l) (when (not (and (r_at ?r ?x) (r_atlander ?l ?y) (r_havesoilanalysis ?r ?p) (r_visible ?x ?y) (r_available ?r) (r_channelfree ?l))) (robot_failed)) (when (and (r_at ?r ?x) (r_atlander ?l ?y) (r_havesoilanalysis ?r ?p) (r_visible ?x ?y) (r_available ?r) (r_channelfree ?l) (not (robot_failed))) (and (not (r_available ?r)) (not (r_channelfree ?l)) (r_channelfree ?l) (r_communicatedsoildata ?p) (r_available ?r))))
    )
     (:action drop
        :parameters (?x - rover ?y - store )
        :precondition (full ?y)
        :effect (and (empty ?y) (not (full ?y)) (when (not (and (r_storeof ?y ?x) (r_full ?y))) (robot_failed)) (when (and (r_storeof ?y ?x) (r_full ?y) (not (robot_failed))) (and (not (r_full ?y)) (r_empty ?y))))
    )
     (:action navigate
        :parameters (?x - rover ?y - waypoint ?z - waypoint )
        :precondition (and (at ?x ?y) (visible ?y ?z) (cantraverse ?x ?y ?z) (available ?x))
        :effect (and (at ?x ?z) (not (at ?x ?y)) (when (not (and (r_cantraverse ?x ?y ?z) (r_available ?x) (r_at ?x ?y) (r_visible ?y ?z))) (robot_failed)) (when (and (r_cantraverse ?x ?y ?z) (r_available ?x) (r_at ?x ?y) (r_visible ?y ?z) (not (robot_failed))) (and (not (r_at ?x ?y)) (r_at ?x ?z))))
    )
     (:action samplerock
        :parameters (?x - rover ?s - store ?p - waypoint )
        :precondition (and (atrocksample ?p) (at ?x ?p) (equippedforrockanalysis ?x) (empty ?s) (storeof ?s ?x))
        :effect (and (full ?s) (haverockanalysis ?x ?p) (not (empty ?s)) (not (atrocksample ?p)) (when (not (and (r_at ?x ?p) (r_atrocksample ?p) (r_equippedforrockanalysis ?x) (r_storeof ?s ?x) (r_empty ?s))) (robot_failed)) (when (and (r_at ?x ?p) (r_atrocksample ?p) (r_equippedforrockanalysis ?x) (r_storeof ?s ?x) (r_empty ?s) (not (robot_failed))) (and (not (r_empty ?s)) (r_full ?s) (r_haverockanalysis ?x ?p) (not (r_atrocksample ?p)))))
    )
     (:action samplesoil
        :parameters (?x - rover ?s - store ?p - waypoint )
        :precondition (and (at ?x ?p) (atsoilsample ?p) (empty ?s) (equippedforsoilanalysis ?x) (storeof ?s ?x))
        :effect (and (havesoilanalysis ?x ?p) (full ?s) (not (empty ?s)) (not (atsoilsample ?p)) (when (not (and (r_at ?x ?p) (r_atsoilsample ?p) (r_equippedforsoilanalysis ?x) (r_storeof ?s ?x) (r_empty ?s))) (robot_failed)) (when (and (r_at ?x ?p) (r_atsoilsample ?p) (r_equippedforsoilanalysis ?x) (r_storeof ?s ?x) (r_empty ?s) (not (robot_failed))) (and (not (r_empty ?s)) (r_full ?s) (r_havesoilanalysis ?x ?p) (not (r_atsoilsample ?p)))))
    )
     (:action takeimage
        :parameters (?r - rover ?p - waypoint ?o - objective ?i - camera ?m - mode )
        :precondition (and (visiblefrom ?o ?p) (calibrated ?i ?r) (supports ?i ?m) (at ?r ?p) (onboard ?i ?r))
        :effect (and (haveimage ?r ?o ?m) (not (calibrated ?i ?r)) (when (not (and (r_calibrated ?i ?r) (r_onboard ?i ?r) (r_equippedforimaging ?r) (r_supports ?i ?m) (r_visiblefrom ?o ?p) (r_at ?r ?p))) (robot_failed)) (when (and (r_calibrated ?i ?r) (r_onboard ?i ?r) (r_equippedforimaging ?r) (r_supports ?i ?m) (r_visiblefrom ?o ?p) (r_at ?r ?p) (not (robot_failed))) (and (r_haveimage ?r ?o ?m) (not (r_calibrated ?i ?r)))))
    )
)