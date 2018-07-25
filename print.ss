
(define println
  (lambda x (for-each display x) (newline)))


(println "(* 100 100)" " => " (* 100 100) )
