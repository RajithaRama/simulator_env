from collections import defaultdict
from mesa_updated.visualization.ModularVisualization import VisualizationElement


class ConversationBox(VisualizationElement):
    """ConversationBox object is used to portray the conversation history of the agents.
    """

    package_includes = ['Conversation.js']


    def __init__(self):
        """Instantiate a new ConversationBox.
        """
        self.js_code = 'elements.push(new ConversationBox());'
        super().__init__()

    def render(self, model):
        """Returns the current conversation history of the agents.
        """
        return model.message_history