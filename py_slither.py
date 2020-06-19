
import pygame
import random
from firebase import firebase
from Objects import Block, Snake
from Hashtable import Hashtable

db_loc = "https://py-slither.firebaseio.com/test"
firebase = firebase.FirebaseApplication(db_loc, None)

""" Firebase Functions:
     get(location, id=None): gives dict of table keys which map the values (of id if given)
     post(location, str): creates a new child of the location entry in table with str value
     put(location, key, value): makes a key-value entry of inputted data in table
     delete(location, id): deletes entry with inputted key id
"""

win_dim = [600,600] #width, height

def computePlayerNum(db_loc):
    if firebase.get(db_loc,'p1') == -1:
        return 1
    return 2
        

def init_game(window):
    p_id = ''
    o_id = ''
    #get status, if status on, break (a game is still running)
    if firebase.get(db_loc,'status') == 1:
        return

    p_num = computePlayerNum(db_loc)
    if p_num == 1:
        p_id = 'p'+str(1)
        o_id = 'p'+str(2)
        firebase.put(db_loc,'p1',-2) #-2 signifies that p1 has joined 
        while(firebase.get(db_loc,'status') == 0):
            continue
    elif p_num == 2:
        p_id = 'p'+str(2)
        o_id = 'p'+str(1)
        firebase.put(db_loc,'status',1) #change status to on
    my_snake = None
    other_snake = None
    food_block = None
    grid_table = Hashtable(win_dim,20) #snakes are 20X20px
    if firebase.get(db_loc,'status') == 1: #if statement just added to force that one player can't get ahead of another
        #make the snakes
        if p_num == 1:
            """ make snake loc in top left corner moving right (3)
                and other snake bottom right corner moving left (2)"""
            my_snake = Snake(win_dim,1)
            other_snake = Snake(win_dim,2)
            grid_table.mark_arr(my_snake.get_chain())
            grid_table.mark_arr(other_snake.get_chain())
            firebase.put(db_loc,'p1',3)
            update_coords(generate_rand_coords(grid_table))
        else:
            my_snake = Snake(win_dim,2)
            other_snake = Snake(win_dim,1)
            grid_table.mark_arr(my_snake.get_chain())
            grid_table.mark_arr(other_snake.get_chain())
            firebase.put(db_loc,'p2',2)
            while firebase.get(db_loc,'food') == '-1,-1':
                continue
    food_block = make_block(firebase.get(db_loc,'food'))
    
    running = True
    while running:
        pygame.time.wait(50)#ms
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                print("I quit the game")
                break
            
        keys = pygame.key.get_pressed()
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            my_snake.change_direction(0)
            firebase.put(db_loc,p_id,0)
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            my_snake.change_direction(1)
            firebase.put(db_loc,p_id,1)            
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            my_snake.change_direction(2)
            firebase.put(db_loc,p_id,2)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            my_snake.change_direction(3)
            firebase.put(db_loc,p_id,3)
        #get other snake direction and update it
        o_dir = firebase.get(db_loc,o_id)
        if o_dir != other_snake.dir():
            other_snake.change_direction(o_dir)

        my_snake.move()
        other_snake.move()
        
        window.fill((0,0,0)) #reset the window
        draw_snake(window, my_snake.get_chain())
        draw_snake(window, other_snake.get_chain())
        draw_food(window, food_block)
        pygame.display.update()

    if p_num == 1:
        reset_DB()

def draw_snake(window, snake_chain):
    for block in snake_chain:
        pygame.draw.rect(window,(255,255,255),(block.xpos(),block.ypos(),block.length(),block.width()))
        
def draw_food(window, food_block):
    pygame.draw.rect(window,(255,0,0),(food_block.xpos(),food_block.ypos(),food_block.length(),food_block.width()))

    #while status is on, run the game. status will be off if a player leaves game (dies or force quit)

def make_block(str_coords):
    coords = make_coords(str_coords)
    return Block(coords[0],coords[1])

def make_str(coords):
    return str(coords[0]) +','+ str(coords[1])

def make_coords(str_coords):
    split = str_coords.find(',')
    xpos = int(str_coords[0:split])
    ypos = int(str_coords[split+1:len(str_coords)])
    return [xpos,ypos]

def update_coords(coords):
    str_coords = make_str(coords)
    firebase.put(db_loc,'food',str_coords)
    
def generate_rand_coords(table):
    open_spots = table.get_unmarked()
    rand_index = random.randint(0,len(open_spots))
    return open_spots[rand_index]

def reset_DB():
    firebase.put(db_loc,'food','-1,-1')
    firebase.put(db_loc,'p1',-1)
    firebase.put(db_loc,'p2',-1)
    firebase.put(db_loc,'status',0)
    
if __name__ == '__main__':
    pygame.init()
    window = pygame.display.set_mode(win_dim)
    init_game(window)
    pygame.quit()
    
