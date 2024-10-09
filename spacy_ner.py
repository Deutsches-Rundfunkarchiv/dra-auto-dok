import spacy
class perform_spacy_analysis():
    """Performs Named_Entity Recognition on single Text or Test List"""

    def __init__(self, model = "de_core_news_sm"):
        """Inputs:
            model(str): Official spacy-name for model to load (defaults to "de_core_news_sm")
            """
        self.model = model
        self.NER = self.load_model()

    def load_model(self):
        """Loads Spacy Model for usage
        
            Returns:
                NER(Spacy Model Object): Ready loaded Spacy Model"""
        NER = spacy.load(self.model)

        return(NER)

    def perform_on_text(self, input_text):
        """Performs Named Entity Recognition on single text
        
        Inputs:
            input_text(str): Text  input fpr named entity analysis
            
        Returns:
            text_ner(json): Entities found as json object"""
        text_ner = self.NER(input_text)

        return(text_ner)
    
    def perform_on_text_list(self, input_textlist):
        """Performs Named Entity Recognition with SpaCy on List of texts
            Inputs:
                input_textlist (list): List of texts to perform named entity recognition on.

            Returns:
                entities_word_all(list): List of words identified as entities
                entities_arten_all(list): List of entity-types for entity word list
        
        """
        entities_arten_all = []
        entities_word_all = []
        for text in input_textlist:
            art_single_text = []
            word_single_text = []
            entities_line = self.perform_on_text(text)
            for ent in entities_line.ents:
                art_single_text.append(ent.label_)
                word_single_text.append(ent.text)
            entities_arten_all.append(art_single_text)
            entities_word_all.append(word_single_text)

        return(entities_word_all, entities_arten_all)
