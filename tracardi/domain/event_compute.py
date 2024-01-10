from typing import Optional, List

from pydantic import BaseModel


class EventCompute(BaseModel):
    run: str  # always, on-profile-change
    func: List

    def run_always(self) -> bool:
        return self.run.lower() == 'always'

    def run_on_profile_change(self) -> bool:
        return self.run.lower() == 'on-profile-change'

    def yield_functions(self):
        for profile_property, compute_string in self.func:
            if not compute_string.startswith("call:"):
                continue

            yield profile_property, compute_string
