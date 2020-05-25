class SectionStructure(CollectionContents):
    # TODO: add functions for creating an empty SectionStructure and modifying it like a dict of list of lists

    def __init__(self, sections: {str: [[BasicShape]]}, section_order: [str], reorderable: bool, section_reorderable: bool):
        self._sections = sections
        self._section_order = section_order
        self._reorderable = reorderable
        self._section_reorderable = section_reorderable

    def get_sections(self) -> {str: [[BasicShape]]}:
        return self._sections

    def get_section_order(self) -> [str]:
        return self._section_order

    def is_reorderable(self) -> bool:
        return self._reorderable

    def is_section_reorderable(self) -> bool:
        return self._section_reorderable

    def reorder(self, section: str, i: int, j: int) -> None:
        if self._reorderable:
            self._sections[section][i], self._sections[section][j] = self._sections[section][j], self._sections[section][i]
        else:
            raise ReorderException()

    def reorder_ml(self, section_index: int, i: int, j: int) -> None:
        self.reorder(self._section_order[section_index], i, j)

    def reorder_section(self, i: int, j: int) -> None:
        if self._section_reorderable:
            self._section_order[i], self._section_order[j] = self._section_order[j], self._section_order[i]
        else:
            raise ReorderException()

    def __len__(self) -> int:
        def length_of_section(section: [[BasicShape]]):
            return sum(len(group) for group in section)

        return sum(length_of_section(section) for section in self._sections.values())

    def __iter__(self) -> BasicShape:
        for section in [self._sections[section] for section in self._section_order]:
            for group in section:
                for element in group:
                    yield element
