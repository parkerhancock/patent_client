from patent_client.util.base.manager import Manager
import math
from .api import PublicSearchApi
from .keywords import keywords

class QueryException(Exception):
    pass

class PublicPatentSearchManager(Manager):
    page_size = 500

    def _get_results(self):
        query = self._get_query()
        order_by = self._get_order_by()
        sources = self.config.options.get("sources", ["US-PGPUB", "USPAT", "USOCR"])
        page_no = 0
        obj_counter = 0
        while True:
            page = PublicSearchApi(
                query=query, 
                start=page_no * self.page_size,
                limit=self.page_size,
                sort=order_by,
                sources=sources
                )
            for obj in page["patents"]:
                if self.config.limit and obj_counter > self.config.limit:
                    break
                yield self.__schema__.load(obj)
                obj_counter += 1
            page_no += 1
            if len(page['patents']) < self.page_size:
                break

    def __len__(self):
        if hasattr(self, "_len"):
            return self._len
        query = self._get_query()
        order_by = self._get_order_by()
        sources = self.config.options.get("sources", ["US-PGPUB", "USPAT", "USOCR"])
        page = PublicSearchApi(
                    query=query, 
                    start=0,
                    limit=self.page_size,
                    sort=order_by,
                    sources=sources
                    )

        total_results = page['totalResults']
        total_results -= self.config.offset
        if self.config.limit:
            self._len = min(self.config.limit, total_results)
        else:
            self._len = total_results
        return self._len


    def _get_order_by(self):
        if not self.config.order_by:
            return "date_publ desc"
        order_str = list()
        for value in self.config.order_by:
            if value.startswith("+"):
                order_str.append(f"{value[1:]} asc")
            elif value.startswith("-"):
                order_str.append(f"{value[1:]} desc")
            else:
                order_str.append(f'{value} asc')
        return " ".join(order_str)
            
        

    def _get_query(self):
        if "query" in self.config.filter:
            return self.config.filter['query']
        query_components = list()
        for key, value in self.config.filter.items():
            if key not in keywords:
                raise QueryException(f"{key} is not a valid search field!")
            query_components.append(f'("{value}")[{keywords[key]}]')
        return " AND ".join(query_components)
