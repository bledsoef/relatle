'use client'

import React, { useEffect, useState } from 'react'
import { Modal, Text, Flex, Group, Card } from '@mantine/core'
import ShareResults from './ShareResults'
import { Artist } from './Game'
import ScrollablePath from './ScrollablePath'
import ArtistInfo from './ArtistInfo'
import Scoreboard from './Scoreboard'
import SharePath from './SharePath'
import Arrow from './Arrow'

export interface GameOverProps {
    opened: boolean,
    close: () => void,
    path: string[],
    guesses: number,
    matchup: string[],
    resets: number,
    web: {[key: string]: Artist},
    is_custom: boolean
}

const GameOver = (props: GameOverProps) => {
    const {opened, close, path, guesses, matchup, resets, web, is_custom} = props
    const [start, end] = matchup

    const calculateTimeLeft = (): { hrs: string; mins: string; secs: string } => {
      const now = new Date()
      const tmrw = new Date(now)
      tmrw.setDate(now.getDate() + 1)
      tmrw.setHours(0,0,0,0)

      const addLeadingZero = (number: number): string => {
        return number < 10 ? `0${number}` : `${number}`;
      }
      
      const timeDiff = tmrw.getTime() - now.getTime();
      const hrs = Math.floor((timeDiff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      const mins = Math.floor((timeDiff % (1000 * 60 * 60)) / (1000 * 60));
      const secs = Math.floor((timeDiff % (1000 * 60)) / 1000);
      
      return { hrs: addLeadingZero(hrs), mins: addLeadingZero(mins), secs: addLeadingZero(secs) };
    }

    const [timeLeft, setTimeLeft] = useState(calculateTimeLeft());
    useEffect(() => {
      const interval = setInterval(() => {
        setTimeLeft(calculateTimeLeft());
      }, 1000);

    // Clean up the interval on component unmount
    return () => clearInterval(interval);
    }, []);

  
  return (
    <Modal opened={opened} 
    onClose={close} withCloseButton={true} centered
    padding="lg" radius="lg"
    title="You Won!"
    styles={{ title: { fontSize: "24px", color: "#f1f3f5", fontWeight: 700 } }}>
      <Flex 
          align="center"
          direction="column"
          gap="lg">
        <Group justify="center">
          <ArtistInfo artist={web[start]} small={true} is_green={false}></ArtistInfo>
          <Arrow small={false} down={false}/>
          <ArtistInfo artist={web[end]} small={true} is_green={true}></ArtistInfo>
        </Group>
        <Scoreboard guesses={guesses} resets={resets} greenBorder={true}/>
        <Text ta="center" size="sm">Your Path</Text>
        <ScrollablePath matchup={matchup} web={web} path={path}></ScrollablePath>
        {!is_custom ?
        <Card shadow="md" radius="lg" p="sm" withBorder>
          <Flex
            gap="0px" justify="center"
            align="center" direction="column"
            wrap="wrap"
          >
            <Text size="sm" ta="center" fw={500}>Time until next matchup</Text>
             <Text c="gray.1" size="lg" fw={700}>{`${timeLeft.hrs}:${timeLeft.mins}:${timeLeft.secs}`}</Text>
          </Flex>
        </Card>
        : null}
        <Group justify="center">
          <SharePath path={path}/>
          <ShareResults path={path} guesses={guesses} matchup={matchup} resets={resets} is_custom={is_custom}/>
        </Group>
      </Flex>
    </Modal>
  )
}

export default GameOver