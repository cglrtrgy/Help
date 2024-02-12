(define (problem merged_problem)
(:domain merged_domain)
(:objects ball1 - ball ball2 - ball ball3 - ball ball4 - ball ball5 - ball left - gripper right - gripper robot_failed - othergoals rooma - room roomb - room roomc - room)
(:init (at ball1 rooma) (at ball2 rooma) (at ball3 roomc) (at ball4 roomb) (at ball5 rooma) (at-robby roomc) (free left) (free right) (r_at ball1 rooma) (r_at ball2 rooma) (r_at ball3 roomc) (r_at ball4 roomb) (r_at ball5 rooma) (r_at-robby roomc) (r_free left) (r_free right))
(:goal
(and
(at ball4 roomb)
(at ball3 roomc)
(at ball2 roomb)
(at ball1 rooma)
(at ball5 rooma)
(not (robot_failed))
)))
