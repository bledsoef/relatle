import React from 'react'
import { Artist, phoneMaxWidth } from './Game'
import { Avatar, Group, Stack, Text } from '@mantine/core'
import ArtistInfo from './ArtistInfo'

export interface RelatedArtistsTitleProps {
    artist: Artist,
    won: boolean,
    endArtist: Artist
}

const RelatedArtistsTitle = React.forwardRef<HTMLDivElement, RelatedArtistsTitleProps>((props, ref) => {
    const {artist, won, endArtist} = props
    let small = window.innerWidth <= phoneMaxWidth

    if (won) {
      return (
        <Stack align="center" gap="xs">
          {won && <Text size={small ? "sm" : "md"}>Tap the scoreboard to view your results</Text>}
          <Group justify="center" gap="xs">
            <Text size={small ? "md" : "lg"}>You found</Text>
            <ArtistInfo artist={endArtist} small={small}/>
          </Group>
        </Stack>
      )
    }

  return (
    <Stack gap='5px' align='center' justify='center'>
      <Group align='center' ref={ref} justify="center" gap="6px">
          <ArtistInfo artist={artist} small={small} is_green={artist.name === endArtist.name}/>
          <Text size={small ? "md" : "lg"}>related artists</Text>
      </Group>
    </Stack>
  )
})
RelatedArtistsTitle.displayName = "RelatedArtistsTitle"

export default RelatedArtistsTitle