

def getListOfAllSpecies(model):
    """
    Returns a list of **ALL** species Ids in the model
    """
    alist = []
    nSpecies = model.getNumSpecies()
    for i in range (nSpecies):
        sp = model.getSpecies(i)
        alist.append (sp.getId())         
    return alist


def getListOfReactionIds (model):
        """
        Returns a list of all reaction Ids.
        """       
        alist = []
        nReactions = model.getNumReactions() 
        for i in range (nReactions):
            p = model.getReaction(i)
            alist.append (p.getId())             
        return alist
    
        
def getNthReactionId (model, index):
        """
        Returns the Id of the nth reaction
        """
        numReactions = model.getNumReactions() 
        if index > numReactions:
            raise Exception ('reaction index does not exist [' + str (index) + ']')
        p = model.getReaction (index)
        return p.getId()


def getNumReactants (model, Id):
        """
         Returns the number of reactants in the reaction given by the Id argument.

        **Parameters**
        
           Id (string): The Id of the reaction in question.

        Example: numProducts = model.getNumReactants ('J1')
        """ 
        p = model.getReaction(Id)
        if p != None:
           return p.getNumReactants()
        raise Exception ('Reaction does not exist')  
        

def getReactant (model, reactionId, reactantIndex):
        """
        Returns the Id of the reactantIndexth reactant in the reaction given by the reactionId

        **Parameters**
        
           Id (string): The Id of the reaction in question
           
           reactantIndex (int): The ith reactant in the reaction

        Example: astr = model.getReactant ('J1', 0)
        """ 
        ra = model.getReaction(reactionId)
        sr = ra.getReactant(reactantIndex)
        return sr.getSpecies()
 
def getProduct (model, reactionId, productIndex):
        """
        Returns the Id of the productIndexth product in the reaction given by the reactionId

        **Parameters**
        
           Id (string): The Id of the reaction in question
           
           productIndex (int): The ith product in the reaction

        Example: astr = model.getProduct ('J1', 0)
        """ 
        ra = model.getReaction(reactionId)
        sr = ra.getProduct(productIndex)
        return sr.getSpecies()
    
    
def getNumProducts (model, Id):
        """
        Returns the number of products in the reaction given by the Id argument.

        **Parameters**
        
           Id (string): The Id of the reaction in question.
           
        Example: numProducts = model.getNumProducts ('J1')
        """ 
        p = model.getReaction(Id)
        if p != None:
           return p.getNumProducts()
        raise Exception ('Reaction does not exist') 
  
  