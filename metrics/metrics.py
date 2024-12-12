from metrics.metrics_preprocessor import MetricsPreprocessor


def catch_division_by_zero(func):
    """
    Wrapper, which ensure that there is no error if there are no positives, leading to division by zero
    """
    def wrapper(self):
        try:
            return func(self)
        except ZeroDivisionError:
            return 0

    return wrapper


class Metrics:
    def __init__(self, metrics_preprocessor: MetricsPreprocessor) -> None:
        """
        Metric calculation, based on the metric proprocessor

        :param MetricsPreprocessor metrics_preprocessor: Preprocessor instance which contains the parsed data
        """
        self.metrics_preprocessor = metrics_preprocessor
        self.true_positives = self.metrics_preprocessor.true_positives
        self.true_negatives = self.metrics_preprocessor.true_negatives
        self.false_positives = self.metrics_preprocessor.false_positives
        self.false_negatives = self.metrics_preprocessor.false_negatives
        self.positives = self.true_positives + self.false_positives
        self.negatives = self.true_negatives + self.false_negatives

    @catch_division_by_zero
    def accuracy(self):
        value = (self.true_positives + self.true_negatives) / (
            self.positives + self.negatives
        )
        return value

    @catch_division_by_zero
    def precision(self):
        value = (self.true_positives) / (self.positives)
        return value

    @catch_division_by_zero
    def inverse_precision(self):
        value = (self.true_negatives) / (self.negatives)
        return value

    @catch_division_by_zero
    def recall(self):
        value = (self.true_positives) / (self.true_positives + self.false_negatives)
        return value

    @catch_division_by_zero
    def inverse_recall(self):
        value = (self.true_negatives) / (self.true_negatives + self.false_positives)
        return value

    @catch_division_by_zero
    def fallout(self):
        value = (self.false_positives) / (self.false_positives + self.true_negatives)
        return value

    @catch_division_by_zero
    def missrate(self):
        value = (self.false_negatives) / (self.false_negatives + self.true_positives)
        return value

    def detection_rate(self):
        # Get attack time intervals
        time_intervals = self.metrics_preprocessor.time_intervals

        # For each interval, check if there is an attack
        value = 0
        start_interval = None
        interval_list = []
        for interval in time_intervals:
            if start_interval == None and time_intervals[interval]["attack"]:
                start_interval = interval
            if start_interval != None and not time_intervals[interval]["attack"]:
                interval_list.append([start_interval, interval])
                start_interval = None

        for pair in interval_list:
            for interval in range(pair[0], pair[1]):
                if time_intervals[interval]["alert"]:
                    value += 1
                    break

        return value / len(interval_list)

    @catch_division_by_zero
    def f_score(self):
        precision = self.precision()
        recall = self.recall()

        value = 2 * (precision * recall) / (precision + recall)
        return value
