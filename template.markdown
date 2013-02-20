@{ for conversation in history -}@
@{ for message in conversation -}@
**@{{message.who}}@:** @{{message.text}}@  
@{ endfor -}@
@{ if not loop.last }@
* * *

@{ endif -}@
@{ endfor -}@
