from py2neo import Graph
from py2neo.matching import *
from pandas.core.common import flatten


class GraphQuery:
    def __init__(self, size_limit=30):
        self.graph = Graph(password='syq4')
        self.nodematcher = NodeMatcher(self.graph)
        self.relmatcher = RelationshipMatcher(self.graph)
        self.size_lim = size_limit

    def findNodebyID(self, ID):
        """
        Return the node by ID
        :param ID: string type
        :return: Node type
        """
        node = self.graph.run("MATCH(n) WHERE n.ChemicalID = \'" +
                         str(ID) + "\' OR n.DiseaseID = \'" + str(ID) + "\' RETURN n").data()
        if not node:
            return None
        else:
            return node[0]['n']

    def findNodeContainName(self, Name):
        nodes = self.graph.run("MATCH (n) WHERE n.ChemicalName CONTAINS \'"+Name
                       +"\' OR n.DiseaseName Contains \'"+Name+"\' RETURN n").data()
        return [node['n'] for node in nodes]


    def findDiseasebyID(self, DiseaseID):
        '''
        find Disease Node by DiseaseID
        :param DiseaseID: string type
        :return: Node type
        '''

        return self.nodematcher.match('Disease', DiseaseID=DiseaseID).first()

    def findChemicalbyID(self, ChemicalID):
        '''
        find Chemical Node by ChemicalID
        :param ChemicalID: string type
        :return: Node type
        '''
        return self.nodematcher.match('Chemical', ChemicalID=ChemicalID).first()

    def findDiseaseParent(self, DiseaseNode):
        '''
        get a list of parents of the Disease Node
        :param DiseaseNode: Node type
        :return: a list contains Parents Node
        '''
        rel_list = self.relmatcher.match([DiseaseNode, None], r_type='ParentDisease').\
            limit(self.size_lim)
        parent_list = [rel.end_node for rel in rel_list]
        return parent_list

    def findDiseaseChild(self, DiseaseNode):
        '''
        get a list of children of the current disease node
        :param DiseaseNode: Node type
        :return: a list of Node type
        '''
        rel_list = self.relmatcher.match([None, DiseaseNode], r_type='ParentDisease').\
            limit(self.size_lim)
        child_list = [rel.start_node for rel in rel_list]
        return child_list

    def findChemicalParent(self, ChemicalNode):
        '''
        get a list parents of the current chemical node
        :param ChemicalNode: Node type
        :return: a list of Node type
        '''
        rel_list = self.relmatcher.match([ChemicalNode, None], r_type='ParentChemical').\
            limit(self.size_lim)
        parent_list = [rel.end_node for rel in rel_list]
        return parent_list

    def findChemicalChild(self, ChemicalNode):
        '''
        get a list of children of the current chemical node
        :param ChemicalNode: Node type
        :return: a list of Node type
        '''
        rel_list = self.relmatcher.match([None, ChemicalNode], r_type='ParentChemical').\
            limit(self.size_lim)
        child_list = [rel.start_node for rel in rel_list]
        return child_list

    def findPaperGivenChemical(self, ChemicalNode, return_node=False):
        '''
        Retrieve the list of papers containing the chemical node
        :param ChemicalNode: Node type
        :return: a list of list with the first column describes the disease
                (Disease Node), the second column be string 'pmids'
        '''
        rel_list = self.relmatcher.match([ChemicalNode, None], r_type='ChemicalDisease')
        if return_node==True:
            paper_list = [ [rel.end_node, rel.get('pmids')] for rel in rel_list]
        else:
            paper_list = [rel.get('pmids') for rel in rel_list]
            paper_list = list(set(flatten(paper_list)))
        return paper_list

    def findPaperGivenDisease(self, DiseaseNode, return_node=False):
        '''
        Retrieve the list of papers containing the desease node
        :param DiseaseNode: Node type
        :return: a list of list with the first column being Chemical Node that
                has effect on the disease, and the second column being the paper with 'pmids'
        '''
        rel_list = self.relmatcher.match([None, DiseaseNode], r_type='ChemicalDisease')
        if return_node==True:
            paper_list = [ [rel.start_node, rel.get('pmids')] for rel in rel_list]
        else:
            paper_list = [rel.get('pmids') for rel in rel_list]
            paper_list = list(set(flatten(paper_list)))
        return paper_list

    def findPaperGivenPair(self, ChemicalNode, DiseaseNode):
        '''
        Retrieve the pmids of papers given the chemical and disease nodes
        :param ChemicalNode: Node type
        :param DiseaseNode: Node type
        :return: a list of strings
        '''
        rel_list = self.relmatcher.match([ChemicalNode, DiseaseNode], r_type='ChemicalDisease')
        paper_list = [rel.get('pmids') for rel in rel_list]
        paper_list = list(set(flatten(paper_list)))
        return paper_list

    def findDiseaseContainName(self, DiseaseName, return_node=False):
        """
        find the disease Node containing the name string
        :param DiseaseName: string type
        :return: a dictionary {key:DiseaseID, value:DiseaseName}
        """
        node_list = self.nodematcher.match('Disease', DiseaseName=CONTAINS(DiseaseName)).\
            limit(self.size_lim).all()
        if return_node==True:
            return node_list

        node_dict = {}
        for node in node_list:
            node_dict[node.get('DiseaseID')] = node.get('DiseaseName')
        return node_dict


    def findChemicalContainName(self, ChemicalName, return_node=False):
        """
        find the chemical Node containing the name string
        :param ChemicalName: string type
        :return: list of Node type
        """
        node_list = self.nodematcher.match('Chemical', ChemicalName=CONTAINS(ChemicalName)).\
            limit(self.size_lim).all()

        if return_node==True:
            return node_list

        node_dict = {}
        for node in node_list:
            node_dict[node.get('ChemicalID')] = node.get('ChemicalName')
        return node_dict

    def findDiseaseGivenChemical(self, ChemicalNode):
        """
        get a list of Disease that affected by the given Chemical
        :param ChemicalNode: Node type
        :return: a list of Node type
        """
        rel_list = self.relmatcher.match([ChemicalNode, None], r_type='ChemicalDisease').\
            limit(self.size_lim)
        disease_list = [rel.end_node for rel in rel_list]
        return disease_list

    def findChemicalGivenDisease(self, DiseaseNode):
        """
        get a list of Chemical nodes that have effect on the Disease
        :param DiseaseNode: Node type
        :return: a list of Node type
        """
        rel_list = self.relmatcher.match([None, DiseaseNode], r_type='ChemicalDisease').\
            limit(self.size_lim)
        chemical_list = [rel.start_node for rel in rel_list]
        return chemical_list

    def findSubgraphFromChemical(self, ChemicalNode):
        rel_list = self.graph.run("MATCH (parent)-[r:ChemicalDisease]->(disease)\
                WHERE (:Chemical {ChemicalID: \'" + ChemicalNode['ChemicalID'] +
                             "\'})-[:ChemicalDisease]->(disease:Disease) AND \
                             (:Chemical {ChemicalID: \'" + ChemicalNode['ChemicalID'] +
                             "\'})-[:ParentChemical]->(parent:Chemical) RETURN r").data()
        parent_target_list = [(rel['r'].start_node['ChemicalID'],
                               rel['r'].end_node['DiseaseID']) for rel in rel_list]
        return parent_target_list

    def findSubgraphFromDisease(self, DiseaseNode):
        rel_list = self.graph.run("MATCH (chemical)-[r:ChemicalDisease]->(parent)\
                    WHERE (:Disease {DiseaseID: \'" + DiseaseNode['DiseaseID'] +
                             "\'})<-[:ChemicalDisease]-(chemical:Chemical) AND \
                             (:Disease {DiseaseID: \'" + DiseaseNode['DiseaseID'] +
                             "\'})-[:ParentDisease]->(parent:Disease) RETURN r").data()
        parent_target_list = [(rel['r'].start_node['ChemicalID'],
                               rel['r'].end_node['DiseaseID']) for rel in rel_list]
        return parent_target_list


# main for test
if __name__ == "__main__":
    print("Hello GraphQuery")

    myQuery = GraphQuery()

    # test cases
    '''
    test_node = myQuery.findDiseasebyID('MESH:D058489')
    child_of_test = myQuery.findDiseaseChild(test_node)
    print(len(child_of_test))
    
    # test case for chemical node

    test_chemical = myQuery.findChemicalbyID('MESH:D019307')
    print(test_chemical)
    child_of_test_chemical = myQuery.findChemicalChild(test_chemical)
    print(len(child_of_test_chemical))
    #print(child_of_test_chemical[0].end_node)
    
    # test case for paper given chemical
    
    test_chemical = myQuery.findChemicalbyID('MESH:C534883')
    print(test_chemical)
    paper_of_chemical = myQuery.findPaperGivenChemical(test_chemical)
    #print(paper_of_chemical[:][1])
    # Retrieve the whole papers
    #column = list(zip(*paper_of_chemical))
    #print(column[1][10])
    print(len(paper_of_chemical))
    
    # test case for paper given disease
    
    test_disease = myQuery.findDiseasebyID('MESH:D058489')
    print(test_disease)
    paper_of_disease = myQuery.findPaperGivenDisease(test_disease)
    print(len(paper_of_disease)) # 456 papers/ Actually 1 paper
    
    
    # test case for paper given pair
    
    test_disease = myQuery.findDiseasebyID('MESH:D011471')
    test_chemical = myQuery.findChemicalbyID('MESH:C534883')
    paper_pair = myQuery.findPaperGivenPair(test_chemical, test_disease)
    print(paper_pair)
    
    # test string match for disease
    test_disease_name = 'hahahah'
    print(myQuery.findDiseaseContainName(test_disease_name, return_node=True))
    
    # test string match for chemical
    test_chemical_name = 'Isoquino'
    print(myQuery.findChemicalContainName(test_chemical_name))
    
    # test case for disease given chemical
    test_chemical = myQuery.findChemicalbyID('MESH:C534883')
    disease_by_chemical_list = myQuery.findDiseaseGivenChemical(test_chemical)
    print(len(disease_by_chemical_list))

    # test case for chemical given disease
    chemical_by_disease_list = myQuery.findChemicalGivenDisease(myQuery.findDiseasebyID('MESH:D058489'))
    print(len(chemical_by_disease_list))
    '''
    test_name = 'Isoquino'
    nodes = myQuery.findNodeContainName(test_name)

    print("Goodbye GraphQuery")