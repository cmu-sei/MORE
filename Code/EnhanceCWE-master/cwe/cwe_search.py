# @OPENSOURCE_HEADER_START@
# MORE Tool 
# Copyright 2016 Carnegie Mellon University.
# All Rights Reserved.
#
# THIS SOFTWARE IS PROVIDED "AS IS," WITH NO WARRANTIES WHATSOEVER.
# CARNEGIE MELLON UNIVERSITY EXPRESSLY DISCLAIMS TO THE FULLEST EXTENT
# PERMITTEDBY LAW ALL EXPRESS, IMPLIED, AND STATUTORY WARRANTIES,
# INCLUDING, WITHOUT LIMITATION, THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT OF PROPRIETARY
# RIGHTS.
#
# Released under a modified BSD license, please see license.txt for full
# terms. DM-0003473
# @OPENSOURCE_HEADER_END@
from abc import ABCMeta, abstractmethod
import collections
from collections import OrderedDict
from nltk.stem.porter import *
import re

class CWESearchLocator:
    """
    This class is the service locator class and provides methods for the CWE search service
    providers i.e. cwe search algorithm and the views. CWE search service providers register
    with the class as a service providers and assign a priority to themselves. The class also
    provides a method for the views to get the service providers with the highest priority.
    """

    highest_priority = 0  # static property to store the highest priority
    service_provider = None  # static property that stores a reference to the highest priority service provider

    @staticmethod
    def register(cwe_search, priority):
        """
        This class method is called by the service providers to register themselves with the
        service locator
        :param cwe_search: a reference to the object that is willing to register itself
        :param priority: the priority, which the object want to assign to itself
        :return: returns 'True' or 'False' depending on whether the registration is success or not
        """

        if isinstance(cwe_search, CWESearchBase):
            if priority > CWESearchLocator.highest_priority:
                CWESearchLocator.highest_priority = priority
                CWESearchLocator.service_provider = cwe_search
                return True
            else:
                return False
        else:
            raise ValueError('Registration as service provider failed: objects, which inherits CWESearchBase can only register as the service provider')

    @staticmethod
    def get_instance():
        """
        This class method is called by the views who wants to get a reference of the highest
        priority service provider
        :return: a reference to the highest priority service provider
        """

        highest_priority_instance = CWESearchLocator.service_provider
        if (highest_priority_instance == None):
            # If no instance is registered, raise LookupError with appropriate error
            raise LookupError('No registered CWESearchBase instance found')

        return highest_priority_instance


class CWESearchBase:
    """
    It is an abstract class acting as an interface for Keyword search module.
    All the cwe search algorithm class must inherit from this class and
    implement all the abstract methods.
    """
    __metaclass__ = ABCMeta

    # Abstract method declaration
    @abstractmethod
    def search_cwes(self, text):
        """
        This is the main abstract method which receives a string and passes the CWE Objects with their match counts
        It also invokes two other methods, i.e, remove_stopwords() and stem_text() to remove redundant words and stem
        the remaining text
        :param text: A string which corresponds to description
        :return: A list of tuples wherein the first item will be a CWE Object and second item will be its match count
        """
        pass

    @abstractmethod
    def remove_stopwords(self, text):
        """
        This abstract method reads stop words from a text file and removes the redundant words like a, an, the from the
        description
        :param text: A string which corresponds to description
        :return: A collection of words from the description from which all the stop words have been removed
        """
        pass

    @abstractmethod
    def stem_text(self, text):
        """
        This abstract method receives a collection of words. It forms a collection of stemmed words and send it to the calling function
        :param text: A collection of words from the description from which all the stop words have been removed
        :return: A collection of stemmed words
        """
        pass


#  Concrete Class definition
class CWEKeywordSearch(CWESearchBase):

    def __init__(self):
        """
        This is a constructor of the class which reads stop words from a file and stores them.
        The words don't need to be read from the disk again and again for every request.
        """

        # Read stop words in a collection from a file stored in the disk
        import os
        self.stop_words = []
        with open(os.getcwd() + '/cwe/stopwords.txt', 'r') as f:
            for line in f:
                for word in line.split():
                    self.stop_words.append(word)


    def search_cwes(self, text):
        """
        This is the concrete implementation of the super class' abstract method
        """
        match_count = []

        # Validate text for None or empty string
        if not text: # is None or text is False:
            return match_count

        if not isinstance(text, basestring):
            raise ValueError('Please pass a string in the text description.')

        # Call Stop Word method here
        filtered_words = self.remove_stopwords(text)

        # Call stemmer here
        stemmed_list = self.stem_text(filtered_words)

        #  Form a dictionary with the count zero
        from cwe.models import CWE
        cwe_list = CWE.objects.filter(keywords__name__in = stemmed_list).distinct()

        #  Count the exact number of occurrences
        for cwe in cwe_list: # iterate over CWEs
            match_count.append((cwe, cwe.keywords.filter(name__in = stemmed_list).count()))

        match_count.sort(key= lambda x: x[1], reverse=True)
        return match_count


    def remove_stopwords(self, text):
        """
        This is the concrete implementation of the super class' abstract method
        """

        # make lower case and remove non-alphanumeric characters except for underscore
        text = text.lower()
        text = re.sub(r'\W+', ' ', text)

        words_in_text = text.split()  # Tokenize the words

        # Remove Stop words
        filtered_words = [word for word in words_in_text if word not in self.stop_words]
        return filtered_words


    def stem_text(self, filtered_words):
        """
        This is the concrete implementation of the super class' abstract method
        """

        st = PorterStemmer()  # Initialize a stemmer

        # Build stemmed list
        stemmed = [st.stem(word) for word in filtered_words]

        # Sort by frequency
        counts = collections.Counter(stemmed)
        stemmed = sorted(stemmed, key=counts.get, reverse=True)

        # Remove duplicates while preserving the order
        stemmed = list(OrderedDict.fromkeys(stemmed))
        return stemmed


# Register a default CWESearchBase object with the service locator
# Note: We are deliberately not handling the exception here, because it is very unlikely
# that the exception will be raised if the correct algorithm is registered properly. If
# not, unhandled exception will make it easier to find the problem.
CWESearchLocator.register(CWEKeywordSearch(), 1)
