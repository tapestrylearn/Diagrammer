def has22(nums):
  return any([nums[i] == 2 and nums[i + 1] == 2 for i in range(len(nums) - 1)])

if __name__ == '__main__':
    print(has22([1, 2, 2, 1, 2, 1, 2, 2]))
    print(has22([2, 2]))
    print(has22([]))
    print(has22([1, 2, 1]))
    print(has22([2]))
