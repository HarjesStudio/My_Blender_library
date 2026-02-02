import bpy
import os
from collections import deque

# Pakolliset perustiedot, jotta lisaosa toimii:
bl_info = {
    "name" : "Import My Library",                   # Nimi, jolla lisaosa nakyy asennusvalikossa
    "author" : "Harriet K",                  
    "version" : (1, 1, 5),                          # Version numero 
    "blender" : (2, 80, 0),                         # Blenderin alin versio jossa toimii 
    "category" : "Import",                          # Kategoria, johon lisa-osa luokitellaan 
    "location" : "3D Viewport",                     # Sijainti Blenderin sisalla
    "description" : "Import my previous meshes",    # Lyhyt kuvaus lisaosan toiminnasta, nakyy add-on valikossa
}


# OSA 1: Maaritetaan muutamia globaaleja muuttujia, jotta niiden sisältämä data saadaan kulkemaan eri luokkien valilla

# Talletetaan kayttajan antama kategorian nimi
bpy.types.Scene.user_input = bpy.props.StringProperty(name="Name", default="new category")
# Talletetaan kayttajan valitsema parent kategoria
bpy.types.Scene.active_category = bpy.props.StringProperty(name="Active Category", default="Root")
# Talletetaan kayttajan valitsema malli
bpy.types.Scene.active_model = bpy.props.StringProperty(name="Active Model", default="Model name")


# Alustetaan muutama muuttuja importtausta varten
# Lahdetiedoston sijainti, tuotavan objektin nimi
# Inner path kertoo etta halutaan tuoda vain ja ainoastaan nimetty objekti, eika esim. koko scenea
file_path = ''          
inner_path = 'Object'   
object_name = ''        




# OSA 2: Luodaan luokat ja funktiot kategorioiden luontia ja kasittelya varten
# Naita luokkia ei rekisteroida ja nimetaan tavanomaisesti (ei caps paalla), jotta ne erottuvat UI luokista


# Luodaan luokka n-ary treelle, joka tulee sisaltamaan kategoriat
class TreeNode:
    
    # Yksittainen node, attribuutteina lapset lista seka noden nimi 
    def __init__(self, name):
        self.name = name 
        self.children = [] 

    # Uuden noden lisaaminen
    def add_child(self, child):
        self.children.append(child)  
        
        
# Taytetaan puu kategorioilla, ala-kategorioilla ja ala-ala-kategorioilla

# maaritetaan root
root = TreeNode("Root") 
# lisataan elaimet
animals = TreeNode("Animals")
root.add_child(animals)
# ihmiset
people = TreeNode("People")
root.add_child(people)
# kasvit
plants = TreeNode("Plants")
root.add_child(plants)
# huonekalut
furniture = TreeNode("Furniture")
root.add_child(furniture)

# alakategoriat elaimille
domestic = TreeNode("Domestic")
wild = TreeNode("Wild")
animals.add_child(domestic)
animals.add_child(wild)
# alakategoriat huonekaluille
big = TreeNode("Big")
small = TreeNode("Small")
furniture.add_child(big)
furniture.add_child(small)

# ala-ala kategoriat piensisustukselle
decor = TreeNode("Decor")
useful = TreeNode("Useful")
small.add_child(decor)
small.add_child(useful)
# ala-ala-kategoria koti-elaimille
dogs = TreeNode("Dogs")
domestic.add_child(dogs)


# Kaytetaan Depth-First-Traverse kategorioiden lapikayntiin
# Piirretaan kategoriat nakyviin yksittain, oksa kerrallaan UI:hin
# Ensimmainen loop pitaa huolen, etta root jatetaan valista selkeyden vuoksi.
def dfs_traverse(layout, root):
    
    for child in root.children:
        traverse_node(layout, child, level=0) 

# Sisennetaan tekstimuotoiset kategoriat, jotta listaa on helpompi lukea
# Jos kategorialla on ala-kategorioita, sen nimi piirretaan tekstina
# Jos kategorialla ei ole ala-kategoroita, sen nimi lahetetaan eteenpain ja siita luodaan nappi (operator)
def traverse_node(layout, node, level):

    indent = "  " * level  

    if node.children:
        row = layout.row()
        row.label(text=f"{indent}{node.name}")

        for child in node.children:
            traverse_node(layout, child, level + 1)  
    
    else:
        row = layout.row()
        op = row.operator("wm.dropdown_operator", text=f"{indent}{node.name}")
        op.category_name = node.name


# Antaa listan, johon on tallennettu kaikki kategoriat oksittain jarjestettyna.
# Kategoriat on talletettu tupleina ("IDENTIFIER", "name", "description"), silla dropdownin enum kasittelee vain tupleja, joissa on kolme string tyypin muuttujaa.
# Kategoriat kulkevat stackin kautta. 
# Listaan lisatty kategoria poistetaan stackista ja sen lapset lisataan sinne kaanteisessa jarjestyksessa, jotta lapikayntijarjestys pysyy oikeana.
def dfs_traverse_categories(root):
    result = [] 
    stack = [root]
    
    while stack:
        node = stack.pop()  
        
        identifier = node.name.upper().replace(" ", "_")
        result.append((identifier, node.name, "description"))
        
        stack.extend(reversed(node.children))  

    return result


# luodaan globaali kategorialista enum_propertya varten
categories = dfs_traverse_categories(root)


# Kaytetaan bfs:saa kategorian hakemiseen
# Kaytetaan silloin kun luodaan uutta kategoriaa
# Parent nodesta tiedetaan vain nimi ja sen kanssa haetaan
# Bfs menetelmana, koska puu on matala mutta levea
# Kirjain koko taytyy ohittaa, aktiivisesta kategoriasta talletettu muuttuja on sen identifier, joka on aina isoilla kirjaimilla
def find_node_bfs(root, name):
    name = name.lower()  
    queue = deque([root])

    while queue:
        node = queue.popleft()
        
        if node.name.lower() == name:  
            return node
        
        queue.extend(node.children)

    return None



# OSA 3: Seuraavat luokat kasittelevat itse 3D mallien tietoja


# Luodaan hash table johon talletetaan malleista seuraavat tiedot: Kategoria, Nimi, Tyyppi ja Kuvaus
# Maaritellaan kooksi 120, koska karkeasti arvioituna malleja on n. 40kpl
# Koska malleja kuitenkin pikkuhiljaa tulee lisaa, niin hashtablen tulee kyeta suurenemaan, kun sen tayttoaste ylittaa 75% 
# Hashaykseen kaytetaan pythonin omaa hash funktiota 

class HashTable:
    def __init__(self, size=120):
        self.size = size
        self.count = 0  
        self.table = [[] for _ in range(self.size)]  

    def hash_function(self, key):
        return hash(key) % self.size  

    def insert(self, key, value):
        if self.count / self.size > 0.75:  
            self.resize_table()

        index = self.hash_function(key)
        self.table[index].append((key, value))
        self.count += 1  


    # Luodaan uusi hashtable jonka koko on kaksi kertaa suurempi kuin vanha
    # Uudelleen hashataan kaikki elementit vanhasta taulusta 
    # Siirretaan ne uuteen tauluun ja poistetaan vanha.
    def resize_table(self):
        new_size = self.size * 2  
        new_table = [[] for _ in range(new_size)]  

        for bucket in self.table:
            for key, value in bucket:
                new_index = hash(key) % new_size
                new_table[new_index].append((key, value))

        self.table = new_table  
        self.size = new_size  

    def get(self, key):
        index = self.hash_function(key)
        for stored_key, stored_value in self.table[index]:
            if stored_key == key:
                return stored_value
        return None

    # Tama funktio palauttaa kaikki pyydettyyn kategoriaan kuuluvat mallit
    # Antaa listan tupleina,jotta sen voi antaa suoraan enum_listaan joka tuo ne UI:hin nakyviin.
    # [IDENTIFIER( name, description)] kaikki string muodossa.
    def get_by_category(self, category_name):
        result = []

        for bucket in self.table:
            for key, model_data in bucket:
                if model_data["category"] == category_name:
                    result.append((key, model_data)) 

        if not result:
            return [("NONE", {"name": "No models found", "type": "", "description": "No models in this category"})]

        return result


# Luodaan hashtable
ht = HashTable()

# Lisataan koirat hashtableen
ht.insert("BRIARD", {"category": "Dogs", "name": "Briard", "type": "Highpoly", "description": "rigged"})
ht.insert("CHIHUAHUA", {"category": "Dogs", "name": "Chihuahua", "type": "Highpoly", "description": "print ready"})
ht.insert("COCKERSPANIEL", {"category": "Dogs", "name": "Cockerspaniel", "type": "Highpoly", "description": "sculpt"})

# Lisataan villielaimet hashtableen
ht.insert("ELEPHANT", {"category": "Wild", "name": "Elephant", "type": "Highpoly", "description": "print ready"})
ht.insert("GIRAFFE", {"category": "Wild", "name": "Giraffe", "type": "Highpoly", "description": "rigged"})
ht.insert("RABBIT", {"category": "Wild", "name": "Rabbit", "type": "Lowpoly", "description": "print ready, hollow"})
ht.insert("RHINO", {"category": "Wild", "name": "Rhino", "type": "Highpoly", "description": "sculpt"})
ht.insert("WHALE", {"category": "Wild", "name": "Whale", "type": "Lowpoly", "description": "rigged"})

# Lisataan ihmiset hashtableen
ht.insert("ADULT_FEMALE", {"category": "People", "name": "Adult_female", "type": "Lowpoly", "description": "rigged"})
ht.insert("ADULT_MALE", {"category": "People", "name": "Adult_male", "type": "Lowpoly", "description": "rigged"})

# Lisataan kasvit hashtableen
ht.insert("DAISY", {"category": "Plants", "name": "Daisy", "type": "Lowpoly", "description": "for particle edit"})
ht.insert("MONSTERA", {"category": "Plants", "name": "Monstera", "type": "Lowpoly", "description": "for particle edit"})
ht.insert("SUNFLOWER", {"category": "Plants", "name": "Sunflower", "type": "Highpoly", "description": "sculpt"})

# Lisataan suuret huonekalut hashtableen
ht.insert("BED", {"category": "Big", "name": "Bed", "type": "Lowpoly", "description": "queen size"})
ht.insert("CHAIR", {"category": "Big", "name": "Chair", "type": "Lowpoly", "description": "simple dining chair"})
ht.insert("SOFA", {"category": "Big", "name": "Sofa", "type": "Highpoly", "description": "two person"})
ht.insert("SOFA_CORNER", {"category": "Big", "name": "Sofa_corner", "type": "Lowpoly", "description": "l-shaped"})
ht.insert("TABLE", {"category": "Big", "name": "Table", "type": "Lowpoly", "description": "dining table, round"})

# Lisataan koristeet hashtableen
ht.insert("PAINTING", {"category": "Decor", "name": "Painting", "type": "Lowpoly", "description": "rococo style frame"})
ht.insert("STATUE", {"category": "Decor", "name": "Statue", "type": "Lowpoly", "description": "monkey"})

# Lisataan kayttoesineet hashtableen
ht.insert("BOWL", {"category": "Useful", "name": "Bowl", "type": "Lowpoly", "description": "fruit bowl"})
ht.insert("CANDLE", {"category": "Useful", "name": "Candle", "type": "Lowpoly", "description": "Pillar candle"})
ht.insert("COFFEE_CUP", {"category": "Useful", "name": "Coffee_cup", "type": "Lowpoly", "description": "english style"})
ht.insert("EYEGLASSES", {"category": "Useful", "name": "Eyeglasses", "type": "Lowpoly", "description": "bulky frame"})
ht.insert("JAR_GLASS", {"category": "Useful", "name": "Jar_glass", "type": "Lowpoly", "description": "jam jar"})
ht.insert("KEYBOARD", {"category": "Useful", "name": "Keyboard", "type": "Lowpoly", "description": "gaming"})
ht.insert("TEAPOT", {"category": "Useful", "name": "Teapot", "type": "Lowpoly", "description": "english style"})
ht.insert("WATER_GLASS", {"category": "Useful", "name": "Water_glass", "type": "Lowpoly", "description": "2 dl, glass"})





# OSA 4: UI luokat jotka tuovat kategoria valikon nakyviin

# Tama luokka on piirtaa kaiken nakyviin
# Tiedoissa on: paneelin otsikko, id, sijainti Blenderissa seka valilehden nimi
class MY_PRECIOUS_PT_Panel(bpy.types.Panel):
    bl_label = "Select Category:"           
    bl_idname = "MYPRECIOUS_PT_Panel"       
    bl_space_type = 'VIEW_3D'               
    bl_region_type = 'UI'                   
    bl_category = "My Mesh Library"         

    # Kutsuu dfs_traversea ja piirtaa sen avulla kategoriat nakyviin halutussa jarjestyksessa.
    def draw(self, context):
        layout = self.layout
        dfs_traverse(layout, root)




# OSA 5: UI luokat jotka tuovat nakyviin kategorian lisays osion


# Oma osio uuden kategorian lisaamiselle
# Toimii "MYPRECIOUS_PT_Panel":n jatkeena
# On oletuksena kiinni, jotta valikko olisi selkeampi lukea
class MY_PRECIOUS_PT_Add_new_category(bpy.types.Panel):
    bl_label = "Options"        
    bl_idname = "Panel_options"
    bl_space_type = "VIEW_3D"       
    bl_region_type = "UI"           
    bl_category = "My Mesh Library"  
    bl_parent_id = "MYPRECIOUS_PT_Panel"
    bl_options = {"DEFAULT_CLOSED"}
    
    

    # Piirtaa nakyviin tarvittavat osiot: kategorian nimeaminen ja lisaaminen
    def draw(self, context):       
        layout = self.layout

        row = layout.row()
        row.label(text="Add a category:") 

        row = layout.row()
        row.prop(context.scene,"user_input") 

        row = layout.row()
        row.operator("wm.dropdown_operator_category") 

        row = layout.row()
        row.operator("wm.text_input_operator") 


    

# Hakee tiedon uuden kategorian nimesta jonka kayttaja on syottanyt seka tiedon valitusta parent kategoriasta
# Hakee parent kategorian nimen perusteella oikean kategorian ja antaa uuden kategorian sen alle.
class MY_PRECIOUS_OT_TextInputOperator(bpy.types.Operator):
    bl_idname = "wm.text_input_operator"
    bl_label = "Create"

    def execute(self, context):
        
        user_input = context.scene.user_input  
        active_category = context.scene.active_category

        parent = find_node_bfs(root, active_category)
        
        new_node = TreeNode(user_input)  
        parent.add_child(new_node)  

        # Lisayksen jalkeen resetoi input kentan ja antaa siihen default arvon
        context.scene.user_input = "new category"  
        return {'FINISHED'}



# Tekee pop-up ikkunaan kategoria valikon, kun valitaan parent kategoriaa uudelle kategorialle
# Kayttaa valmista kategoria listaa
# Lisaa uuden kategorian
class  MY_PRECIOUS_OT_DropDownOperator_Category(bpy.types.Operator):
    bl_label = "Select a parent category"                            
    bl_idname = ("wm.dropdown_operator_category")            
    bl_description = ("Open up a dropdown")         

    preset_enum : bpy.props.EnumProperty(           
        name= "",
        description= "Select an option",
        items= categories
    )


    # Avaa pop-up ikkunan
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "preset_enum") 
    
    def execute(self, context):
        # Paivitetaan globaali muuttuja (valittu parent kategoria)
        context.scene.active_category = self.preset_enum
        return {'FINISHED'}

    
# Seuraavat UI luokat koskevat 3D mallien importausta

# Hakee halutun 3D mallin
# Asettaa tuodun mallin aktiiviseksi seka asettaa sen sijainnin 3D kursoriin
class MY_PRECIOUS_OT_AddObjectOperator(bpy.types.Operator):                                              
    bl_idname = "object.add_object"                                    
    bl_label = "Add objects"
    bl_options = {'REGISTER', 'UNDO'}
   
    def execute(self, context):                                         
        bpy.ops.wm.append(
        filepath=os.path.join(file_path, inner_path, object_name),
        directory=os.path.join(file_path, inner_path),
        filename=object_name
        ) 

        objekti = bpy.data.objects[object_name]                        
        bpy.context.view_layer.objects.active = objekti
        bpy.context.active_object.location=bpy.context.scene.cursor.location
        
        return {'FINISHED'}

# Aktivoituu kun kayttaja valitsee jonkun kategorian importtausta varten
# Tama luokka avaa dropdown valikon erilliseen pop-up ikkunaan
# Kategorian nimi tulee ulkopuolelta
class MY_PRECIOUS_OT_DropDownOperator(bpy.types.Operator):
    bl_label = "Select a 3D-model:"                            
    bl_idname = "wm.dropdown_operator"            
    bl_description = "Open up a dropdown"         
    
    category_name: bpy.props.StringProperty()

    def get_enum_items(self, context):

        if not self.category_name:  
            return [("NONE", "No models found", "No models in this category")]

        models = ht.get_by_category(self.category_name)  

        return [(identifier, data["name"], f"{data['type']} {data['description']}")
                for identifier, data in models] or [("NONE", "No models found", "No models in this category")]

    preset_enum: bpy.props.EnumProperty(
        name="",
        description="Select an option",
        items=get_enum_items  
    )

    def invoke(self, context, event):
        models = ht.get_by_category(self.category_name)  
    
        print(f"Models found for category '{self.category_name}': {models}")  

        if not models:
            self.report({'ERROR'}, f"No models found in category '{self.category_name}'")
            return {'CANCELLED'}

        return context.window_manager.invoke_props_dialog(self)


    def draw(self, context):
        layout = self.layout
        layout.label(text=f"Select a 3D-model from {self.category_name}:")
        layout.prop(self, "preset_enum")

    def execute(self, context):
        global object_name
        global file_path

        # HUOM: Kaksi kenoviivaa jokaisessa valissa! Muista myos tiedostopaate .blend!
        file_path = f'C:\\Users\\Harriet\\Desktop\\my_mesh_library\\library{self.category_name}.blend'
        
        model_data = ht.get(self.preset_enum)

        object_name = model_data["name"]
        bpy.ops.object.add_object()   
            
  
        return {'FINISHED'}




# Kaydaan lapi kun lisaosa otetaan kayttoon, vain UI luokat rekisteroidaan
def register():
    
    bpy.utils.register_class(MY_PRECIOUS_PT_Panel),
    bpy.utils.register_class(MY_PRECIOUS_OT_DropDownOperator),
    bpy.utils.register_class(MY_PRECIOUS_OT_AddObjectOperator),
    bpy.utils.register_class(MY_PRECIOUS_PT_Add_new_category),
    bpy.utils.register_class(MY_PRECIOUS_OT_DropDownOperator_Category),
    bpy.utils.register_class(MY_PRECIOUS_OT_TextInputOperator),
    
# Kaydaan lapi kun lisaosa otetaan pois kaytosta
def unregister():
    
    bpy.utils.unregister_class(MY_PRECIOUS_PT_Panel),
    bpy.utils.unregister_class(MY_PRECIOUS_OT_DropDownOperator),
    bpy.utils.unregister_class(MY_PRECIOUS_OT_AddObjectOperator),
    bpy.utils.unregister_class(MY_PRECIOUS_PT_Add_new_category),
    bpy.utils.unregister_class(MY_PRECIOUS_OT_DropDownOperator_Category),
    bpy.utils.unregister_class(MY_PRECIOUS_OT_TextInputOperator),
    del bpy.types.Scene.user_input


if __name__ == "__main__":
    register()