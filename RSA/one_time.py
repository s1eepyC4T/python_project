#File for generate Keys. One time use.

import key_gen as kg

# kg.genKeyPair("A", 763)
# kg.genKeyPair("B", 763)
# kg.genKeyPair("CA", 763)
kg.givePublicKeyFrom_to("A","B")
kg.givePublicKeyFrom_to("B","A")
kg.givePublicKeyFrom_to("CA","A")
kg.givePublicKeyFrom_to("CA","B")