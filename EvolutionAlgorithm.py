from capture import runGames, readCommand, MP
import random, copy
from pathos import multiprocessing as mp
import numpy as np
#import multiprocessing as mp

class Options(object):
    def __init__( self, redOpts = '', blueOpts = '', catchExceptions = False, blue_name = 'Blue', \
                  numTraining = 0, replay = None, super_quiet = False,blue = 'baselineTeam', \
                  red_name = 'Red', layout = 'defaultCapture', numGames = 2, red = 'baselineTeam',\
                  textgraphics = False, fixRandomSeed = True, keys1 = False, keys0 = False, keys3 = False,\
                  keys2 = False, quiet = True, record = False, time = 1200, zoom = 1, Param_Weights_1 = None,\
                  Param_Weights_2 = None, serial_num = None ):
        self.redOpts = redOpts
        self.blueOpts = blueOpts
        self.catchExceptions = catchExceptions
        self.blue_name = blue_name
        self.numTraining = numTraining 
        self.replay = replay
        self.super_quiet = super_quiet
        self.blue = blue
        self.red_name = red_name
        self.layout = layout
        self.numGames = numGames
        self.red = red
        self.textgraphics = textgraphics
        self.fixRandomSeed = fixRandomSeed
        self.keys1 = keys1
        self.keys0 = keys0
        self.keys3 = keys3
        self.keys2 = keys2
        self.quiet = quiet
        self.record = record
        self.time = time
        self.zoom = zoom 
        self.Param_Weights_1 = Param_Weights_1
        self.Param_Weights_2 = Param_Weights_2
        self.serial_num = serial_num 

class EvolutionAlgorithm(object):
    def __init__( self, alpha = 0.6, NumUnit = 30, EnemiesAgentList = None, BasicAgent = None ):
        self.BasicAgent = BasicAgent
        self.EnemiesAgentList = EnemiesAgentList
        if self.EnemiesAgentList is None: 
            self.EnemiesAgentList = [ "enemy3" , "myTeam_caesar", "enemy1", "enemy2", ]          
            #self.EnemiesAgentList = [ "myTeam_caesar", ]          
         
        self.NumUnit = NumUnit
        self.alpha = alpha
        self.evolution_generations = 500                 

    def set_initial_weights( self ):
        initial_command_list = []
        agent_weights_dict = dict()
        for i in range( self.NumUnit ):
            initial_weights_1 = dict()
            initial_weights_1['eats-invader'] = round(random.random()*10,2)
            initial_weights_1['invaders-1-step-away'] = round(random.random()*5,2)
            initial_weights_1['teammateDist'] = round(random.random()*5,2)
            initial_weights_1['closest-food'] = round(-random.random()*5,2)
            initial_weights_1['eats-capsules'] = round(random.random()*20,2)
            initial_weights_1['#-of-dangerous-ghosts-1-step-away'] = round(-random.random()*40,2)
            initial_weights_1['eats-ghost'] = round(random.random()*3,2)
            initial_weights_1['#-of-harmless-ghosts-1-step-away'] = round(random.random(),2)
            initial_weights_1['stopped'] = round(-random.random()*10,2)
            initial_weights_1['eats-food'] = round(random.random()*3,2)
            initial_weights_2 = dict()
            initial_weights_2['eats-invader'] = round(random.random()*10,2)
            initial_weights_2['invaders-1-step-away'] = round(random.random()*5,2)
            initial_weights_2['teammateDist'] = round(random.random()*5,2)
            initial_weights_2['closest-food'] = round(-random.random()*5,2)
            initial_weights_2['eats-capsules'] = round(random.random()*20,2)
            initial_weights_2['#-of-dangerous-ghosts-1-step-away'] = round(-random.random()*40,2)
            initial_weights_2['eats-ghost'] = round(random.random()*3,2)
            initial_weights_2['#-of-harmless-ghosts-1-step-away'] = round(random.random(),2)
            initial_weights_2['stopped'] = round(-random.random()*10,2)
            initial_weights_2['eats-food'] = round(random.random()*3,2)
            agent_weights_dict[ i ] = ( initial_weights_1, initial_weights_2 )
                 
        return agent_weights_dict
    
    def convert_weights_to_option( self, agent_weights_dict):
        argv_list = [] 
        command_list = []
        for agent_index, weights in agent_weights_dict.items():
            weights_1, weights_2 = weights
	    for index, EnemiesAgent in enumerate(self.EnemiesAgentList):
		argv = Options(red=self.BasicAgent, blue=EnemiesAgent, Param_Weights_1=weights_1, Param_Weights_2=weights_2, serial_num=(agent_index,index) )
		argv_list.append( argv )
                #command = readCommand( dict_argv = argv )                 
		#command_list.append( command )        
        return argv_list 

    def evaluate( self, argv_list ):
        score_mat = np.zeros( [ self.NumUnit, len( self.EnemiesAgentList ) ] )
        #consequence = runGames( **command_list[1] )
        #print consequence[0][0].state.data.score 
        #for i in range(len(argv_list)):
        #    games, serial_num = MP( argv_list[i])
        #    print serial_num, games[0].state.data.score
        #raise Exception 
        print "c"*50
        p = mp.ProcessPool( 32 )
        results = []
        for argv in argv_list:
            #print "argv", argv
            results.append( p.apipe( MP, argv ) ) 
        for r in results:
            c = r.get() 
            scores, redWinRate, blueWinRate, serial_num = c
            score_mat[ serial_num ] = sum( scores ) / float( len( scores ) )
        score_array = np.sum( score_mat, 1 )  

        return score_array, score_mat
       
    def champion( self, agent_score_pair_list, agent_weights_dict ):
        agent_score_pair_list = list( zip( list( range( len( agent_score_pair_list ) ) ), agent_score_pair_list ) )
        selected_agent_score_pair_list = sorted( agent_score_pair_list, key = lambda x: x[-1], reverse = True)[ : self.NumUnit / 2 ]        
        print "selected_agent_score_pair_list", selected_agent_score_pair_list

        selected_sorted_weights_list = []      
        for agent_index, score in selected_agent_score_pair_list:
            selected_sorted_weights_list.append( agent_weights_dict[ agent_index ] )
        return selected_sorted_weights_list
              
    def mutation( self, weights_list, mu=0, sigma=1 ):
        if len( weights_list ) != self.NumUnit / 2:
            raise Exception( " Left weights is not equal to half the NumUnit")
 	else:
            new_weights_list = [] 
            for i,weights in enumerate(weights_list):                
                print i
                new_weights_1 = dict()
                for k, v in weights[0].items():
                    v += random.gauss( mu, sigma ) 
                    new_weights_1[k] = v
                new_weights_2 = dict()
                for k, v in weights[1].items():
                    v += random.gauss( mu, sigma ) 
                    new_weights_2[k] = v
                new_weights = ( new_weights_1, new_weights_2 )
                new_weights_list.append( new_weights )   
            
            all_weights_list = weights_list + new_weights_list    
            agent_weights_dict = dict()
            for index, weights in enumerate( all_weights_list ):
                agent_weights_dict[index] = weights
     
 	    return agent_weights_dict 

    def evolution( self ):
        agent_weights_dict = self.set_initial_weights()
        store_scores = []
        for iters in range( self.evolution_generations ):
            print iters 
            print "1"
            argv_list = self.convert_weights_to_option( agent_weights_dict )
            print "2"
            agent_score_pair_list, score_mat = self.evaluate( argv_list )
            print "3" 
            store_scores.append( agent_score_pair_list )
            selected_sorted_weights_list = self.champion( agent_score_pair_list, agent_weights_dict )
            raise Exception
            print "selected_sorted_weights_list"
            agent_weights_dict = self.mutation( selected_sorted_weights_list )  
            print agent_weights_dict   
            print "4" 
            with open("score.txt","a") as f:
                 f.write( str(agent_score_pair_list) )
                 f.write( "\n\n\n" )
            f.close() 

        return agent_weights_dict, np.array( store_scores )

def main():
    ea = EvolutionAlgorithm( BasicAgent = "myTeamBasic" )
    agent_weights_dict, store_scores = ea.evolution() 
    with open("agent_weights_dict.txt","w") as f:
         f.write( str(agent_weights_dict) )
         f.write("\n\n\n")
         f.write( str(store_scores) )
    f.close() 
    np.save( "score.npy", store_scores )

if __name__=="__main__":
    main()

