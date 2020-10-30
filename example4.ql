2 3 +

: square
  dup *
;

square

: count-down
  dup print 1 -
  dup 0 ==
  unless count-down
;

count-down
