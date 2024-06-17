from dataclasses import dataclass, field
from datetime import datetime, timedelta
import csv
import random


def random_timestamp():
    start = datetime.now()
    end = start - timedelta(hours=1)
    delta = end - start
    random_seconds = random.uniform(0, delta.total_seconds())
    return start + timedelta(seconds=random_seconds)


@dataclass
class POI:
    title: str
    map: int
    url: str
    comment: str
    last_used: datetime = datetime.now()

    def __str__(self):
        return f"{self.title} ({self.url})"

    def __repr__(self):
        return self.__str__()

    def last_used_str(self):
        return f"{self.last_used}-{self.title}"


@dataclass
class POIs:
    pois: list[POI] = field(default_factory=list)

    def get_pois_by_level(self, map_level=1):
        self.order_by_last_used()
        return POIs([poi for poi in self.pois if poi.map >= map_level])

    def order_by_last_used(self):
        self.pois.sort(key=lambda x: x.last_used, reverse=True)

    def __str__(self):
        return "\n".join([poi.last_used_str() for poi in self.pois])

    def __repr__(self):
        return self.__str__()

    def get_random_poi(self, map_level=1) -> POI:
        current_time = datetime.now()
        pois = self.get_pois_by_level(map_level)
        ages = [(current_time - poi.last_used).total_seconds() for poi in pois.pois]
        weights = [age / sum(ages) for age in ages][::-1]
        return random.choices(pois.pois, weights=weights, k=1)


def read_pois(filename) -> POIs:
    reader = csv.DictReader(open('data/poi.csv', 'r', encoding='utf-8'))
    pois = POIs()
    for row in reader:
        try:
            pois.pois.append(POI(row['title'], int(row['map']), row['url'], row['comment']))
            #pois.pois.append(POI(row['title'], int(row['map']), row['url'], row['comment'], random_timestamp())) # For testing
        except ValueError:
            print(f"Error reading {row} ({row['map']} not a number); skipping")
            continue
    return pois


if __name__ == "__main__":
    pois = read_pois('data/poi.csv')
    #print(pois.get_pois_by_level())
    print(pois.get_random_poi())
