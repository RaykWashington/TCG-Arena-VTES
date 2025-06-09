map({
  id: string(.id),
  face: {
    front: {
      name: ._name,
      type: if(.types.0 == "Vampire" or .types.0 == "Imbued", "Crypt", .types.0),
    cost: if(.capacity == null, 0, .capacity),
    image: .url,
    isHorizontal: false
  },
   back: if(.types.0 == "Vampire" or .types.0 == "Imbued",{
     name: ._name,
     type: if(.types.0 == "Vampire" or .types.0 == "Imbued", "Crypt", .types.0),
    cost: string(.capacity),
    image: "https://static.krcg.org/card/cardbackcrypt.jpg"
   },"")
  },
  name: ._name,
  type: .types.0,
  capacity: if(.capacity == null, 0 , number(.capacity)),
  clan: if(.clans==null," ", string(.clans)),
  group: number(.group),
  set: string(substring(.ordered_sets, .ordered_sets.length-1)),
  title: if(.title==null, "", .title),
  disciplines: if(.disciplines == null, [" "], split(string(.disciplines), ","))
}) | keyBy(string(.id))